# Copyright 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright 2015 Agile Business Group <http://www.agilebg.com>
# Copyright 2016 Grupo ESOC Ingenieria de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
import shutil
import socket
import traceback
from contextlib import contextmanager
from datetime import datetime, timedelta
from glob import iglob
from pathlib import PurePosixPath
from stat import S_ISDIR

import paramiko
from paramiko import HostKeys
from paramiko.hostkeys import HostKeyEntry, InvalidHostKey
from paramiko.ssh_exception import SSHException

from odoo import _, api, exceptions, fields, models, tools
from odoo.exceptions import UserError
from odoo.service import db

_logger = logging.getLogger(__name__)

#: OpenSSH key type prefixes understood by paramiko.
_KEY_TYPE_PREFIXES = ("ecdsa-", "sk-", "ssh-")

_SFTP_TIMEOUT = 60
_KNOWN_HOSTS = "~/.ssh/known_hosts"


class _SftpClient:
    """Minimal SFTP client over paramiko that applies the host key policy.

    ``paramiko.SSHClient`` cannot express a per-record pinned host key, so the
    transport is built from a socket to keep the timeout and the ``hostkey``
    argument under control.
    """

    def __init__(self, record):
        self._record = record
        self._transport = None
        self._sftp = None

    def __enter__(self):
        rec = self._record
        hostkey = None
        hostkeys = rec._get_sftp_host_keys()
        if hostkeys is not None:
            keys = hostkeys.lookup(rec.sftp_host)
            if not keys:
                raise SSHException(f"No hostkey for host {rec.sftp_host} found.")
            hostkey = next(iter(keys.values()))
        sock = socket.create_connection(
            (rec.sftp_host, rec.sftp_port or 22), _SFTP_TIMEOUT
        )
        sock.settimeout(_SFTP_TIMEOUT)
        self._transport = paramiko.Transport(sock)
        try:
            if rec.sftp_private_key:
                key = paramiko.PKey.from_path(
                    rec.sftp_private_key, passphrase=rec.sftp_password or None
                )
                self._transport.connect(
                    username=rec.sftp_user, pkey=key, hostkey=hostkey
                )
            else:
                self._transport.connect(
                    username=rec.sftp_user,
                    password=rec.sftp_password,
                    hostkey=hostkey,
                )
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
        except Exception:
            self.close()
            raise
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        if self._sftp:
            self._sftp.close()
            self._sftp = None
        if self._transport:
            self._transport.close()
            self._transport = None

    def makedirs(self, path):
        """Create a remote directory and its parents when missing."""
        missing = []
        current = PurePosixPath(path)
        while current != current.parent:
            try:
                attributes = self._sftp.stat(str(current))
            except FileNotFoundError:
                missing.append(current)
                current = current.parent
                continue
            if not S_ISDIR(attributes.st_mode):
                raise OSError(f"{current} is not a directory")
            break
        for directory in reversed(missing):
            self._sftp.mkdir(str(directory))

    def open(self, *args, **kwargs):
        return self._sftp.open(*args, **kwargs)

    def listdir(self, path):
        return self._sftp.listdir(path)

    def unlink(self, path):  # pylint: disable=method-required-super
        return self._sftp.unlink(path)


class DbBackup(models.Model):
    _description = "Database Backup"
    _name = "db.backup"
    _inherit = "mail.thread"

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "Cannot duplicate a configuration."),
        (
            "days_to_keep_positive",
            "CHECK(days_to_keep >= 0)",
            "I cannot remove backups from the future. Ask Doc for that.",
        ),
    ]

    name = fields.Char(
        compute="_compute_name",
        store=True,
        help="Summary of this backup process",
    )
    folder = fields.Char(
        default=lambda self: self._default_folder(),
        help="Absolute path for storing the backups",
        required=True,
    )
    days_to_keep = fields.Integer(
        required=True,
        default=0,
        help="Backups older than this will be deleted automatically. "
        "Set 0 to disable autodeletion.",
    )
    method = fields.Selection(
        [("local", "Local disk"), ("sftp", "Remote SFTP server")],
        default="local",
        help="Choose the storage method for this backup.",
    )
    sftp_host = fields.Char(
        "SFTP Server",
        help=(
            "The host name or IP address from your remote"
            " server. For example 192.168.0.1"
        ),
    )
    sftp_port = fields.Integer(
        "SFTP Port",
        default=22,
        help="The port on the FTP server that accepts SSH/SFTP calls.",
    )
    sftp_user = fields.Char(
        "Username in the SFTP Server",
        help=(
            "The username where the SFTP connection "
            "should be made with. This is the user on the external server."
        ),
    )
    sftp_password = fields.Char(
        "SFTP Password",
        help="The password for the SFTP connection. If you specify a private "
        "key file, then this is the password to decrypt it.",
    )
    sftp_private_key = fields.Char(
        "Private key location",
        help="Path to the private key file. Only the Odoo user should have "
        "read permissions for that file.",
    )
    sftp_host_keys = fields.Text(
        "SFTP Host Keys",
        help="One public key per line, in OpenSSH format, e.g. the output of "
        "'ssh-keyscan'. When set, it replaces the known_hosts file of the "
        "Odoo user.",
    )
    sftp_ignore_hostkey = fields.Boolean(
        "Ignore Host Key",
        help="Skip the SFTP server identity check. Unsafe: only for servers "
        "whose host key cannot be obtained.",
    )

    backup_format = fields.Selection(
        [
            ("zip", "zip (includes filestore)"),
            ("dump", "pg_dump custom format (without filestore)"),
        ],
        default="zip",
        help="Choose the format for this backup.",
    )

    @api.model
    def _default_folder(self):
        """Default to ``backups`` folder inside current server datadir."""
        return os.path.join(tools.config["data_dir"], "backups", self.env.cr.dbname)

    @api.depends("folder", "method", "sftp_host", "sftp_port", "sftp_user")
    def _compute_name(self):
        """Get the right summary for this job."""
        for rec in self:
            if rec.method == "local":
                rec.name = "%s @ localhost" % rec.folder
            elif rec.method == "sftp":
                rec.name = "sftp://%s@%s:%d%s" % (
                    rec.sftp_user,
                    rec.sftp_host,
                    rec.sftp_port,
                    rec.folder,
                )

    @api.constrains("folder", "method")
    def _check_folder(self):
        """Do not use the filestore or you will backup your backups."""
        for record in self:
            if record.method == "local" and record.folder.startswith(
                tools.config.filestore(self.env.cr.dbname)
            ):
                raise exceptions.ValidationError(
                    _(
                        "Do not save backups on your filestore, or you will "
                        "backup your backups too!"
                    )
                )

    def action_sftp_test_connection(self):
        """Check if the SFTP settings are correct."""
        try:
            # Just open and close the connection
            with self.sftp_connection():
                raise UserError(_("Connection Test Succeeded!"))
        except (
            paramiko.AuthenticationException,
            paramiko.SSHException,
            OSError,
        ) as exc:
            _logger.info("Connection Test Failed!", exc_info=True)
            raise UserError(_("Connection Test Failed!")) from exc

    def action_backup(self):
        """Run selected backups."""
        backup = None
        successful = self.browse()

        # Start with local storage
        for rec in self.filtered(lambda r: r.method == "local"):
            filename = self.filename(datetime.now(), ext=rec.backup_format)
            with rec.backup_log():
                # Directory must exist
                try:
                    os.makedirs(rec.folder, exist_ok=True)
                except OSError as exc:
                    _logger.exception("Action backup - OSError: %s" % exc)

                with open(os.path.join(rec.folder, filename), "wb") as destiny:
                    # Copy the cached backup
                    if backup:
                        with open(backup) as cached:
                            shutil.copyfileobj(cached, destiny)
                    # Generate new backup
                    else:
                        db.dump_db(
                            self.env.cr.dbname, destiny, backup_format=rec.backup_format
                        )
                        backup = backup or destiny.name
                successful |= rec

        # Ensure a local backup exists if we are going to write it remotely
        sftp = self.filtered(lambda r: r.method == "sftp")
        if sftp:
            for rec in sftp:
                filename = self.filename(datetime.now(), ext=rec.backup_format)
                with rec.backup_log():
                    cached = db.dump_db(
                        self.env.cr.dbname, None, backup_format=rec.backup_format
                    )

                    with cached:
                        with rec.sftp_connection() as remote:
                            # Directory must exist
                            remote.makedirs(rec.folder)

                            # Copy cached backup to remote server
                            with remote.open(
                                os.path.join(rec.folder, filename), "wb"
                            ) as destiny:
                                shutil.copyfileobj(cached, destiny)
                        successful |= rec

        # Remove old files for successful backups
        successful.cleanup()

    @api.model
    def action_backup_all(self):
        """Run all scheduled backups."""
        return self.search([]).action_backup()

    @contextmanager
    def backup_log(self):
        """Log a backup result."""
        try:
            _logger.info("Starting database backup: %s", self.name)
            yield
        except Exception:
            _logger.exception("Database backup failed: %s", self.name)
            escaped_tb = tools.html_escape(traceback.format_exc())
            self.message_post(  # pylint: disable=translation-required
                body=f"<p>{_('Database backup failed.')}</p><pre>{escaped_tb}</pre>",
                subtype_id=self.env.ref("auto_backup.mail_message_subtype_failure").id,
            )
        else:
            _logger.info("Database backup succeeded: %s", self.name)
            self.message_post(body=_("Database backup succeeded."))

    def cleanup(self):
        """Clean up old backups."""
        now = datetime.now()
        for rec in self.filtered("days_to_keep"):
            with rec.cleanup_log():
                bu_format = rec.backup_format
                file_extension = bu_format == "zip" and "dump.zip" or bu_format
                oldest = self.filename(
                    now - timedelta(days=rec.days_to_keep), bu_format
                )

                if rec.method == "local":
                    for name in iglob(
                        os.path.join(rec.folder, "*.%s" % file_extension)
                    ):
                        if os.path.basename(name) < oldest:
                            os.unlink(name)

                elif rec.method == "sftp":
                    with rec.sftp_connection() as remote:
                        for name in remote.listdir(rec.folder):
                            if (
                                name.endswith(".%s" % file_extension)
                                and os.path.basename(name) < oldest
                            ):
                                remote.unlink(f"{rec.folder}/{name}")

    @contextmanager
    def cleanup_log(self):
        """Log a possible cleanup failure."""
        self.ensure_one()
        try:
            _logger.info(
                "Starting cleanup process after database backup: %s", self.name
            )
            yield
        except Exception:
            _logger.exception("Cleanup of old database backups failed: %s")
            escaped_tb = tools.html_escape(traceback.format_exc())
            self.message_post(  # pylint: disable=translation-required
                body=f"<p>{_('Cleanup of old database backups failed.')}</p>"
                f"<pre>{escaped_tb}</pre>",
                subtype_id=self.env.ref("auto_backup.failure").id,
            )
        else:
            _logger.info("Cleanup of old database backups succeeded: %s", self.name)

    @staticmethod
    def filename(when, ext="zip"):
        """Generate a file name for a backup.

        :param datetime.datetime when:
            Use this datetime instead of :meth:`datetime.datetime.now`.
        :param str ext: Extension of the file. Default: dump.zip
        """
        return "{:%Y_%m_%d_%H_%M_%S}.{ext}".format(
            when, ext="dump.zip" if ext == "zip" else ext
        )

    def _known_hosts_path(self):
        """Return the known_hosts file of the Odoo OS user."""
        return os.path.expanduser(_KNOWN_HOSTS)

    def _get_sftp_host_keys(self):
        """Return the HostKeys to verify the server against, or None to skip.

        Precedence: pinned keys, known_hosts fallback, explicit bypass.
        """
        if self.sftp_ignore_hostkey:
            _logger.warning(
                "Host key verification disabled for the SFTP server %s", self.sftp_host
            )
            return None
        hostkeys = HostKeys()
        if self.sftp_host_keys:
            for key_type, key in self._parse_sftp_host_keys().items():
                hostkeys.add(self.sftp_host, key_type, key)
        elif os.path.isfile(self._known_hosts_path()):
            hostkeys.load(self._known_hosts_path())
        if not hostkeys:
            raise UserError(
                _(
                    "No host key available to verify the SFTP server %(host)s. "
                    "Fill in 'SFTP Host Keys' with the output of 'ssh-keyscan "
                    "%(host)s', or enable 'Ignore Host Key'.",
                    host=self.sftp_host,
                )
            )
        return hostkeys

    def _parse_sftp_host_keys(self):
        """Return ``{key type: paramiko key}`` parsed from the field."""
        keys = {}
        for index, raw_line in enumerate((self.sftp_host_keys or "").splitlines(), 1):
            line = raw_line.strip()
            if not line or line.startswith(("#", "@")):
                continue
            tokens = line.split()
            # Accept "ssh-keyscan" lines and bare keys; the key is bound to
            # the configured host, so any host name in the line is ignored.
            if len(tokens) > 1 and tokens[1].startswith(_KEY_TYPE_PREFIXES):
                tokens = tokens[1:]
            elif not tokens[0].startswith(_KEY_TYPE_PREFIXES):
                raise UserError(
                    _(
                        "Invalid host key on line %(line)s: %(key)s",
                        line=index,
                        key=line,
                    )
                )
            try:
                entry = HostKeyEntry.from_line(
                    f"{self.sftp_host} {' '.join(tokens[:2])}", index
                )
            except (InvalidHostKey, SSHException) as error:
                raise UserError(
                    _(
                        "Invalid host key on line %(line)s: %(key)s",
                        line=index,
                        key=error,
                    )
                ) from error
            if entry is None:
                raise UserError(
                    _(
                        "Unsupported host key on line %(line)s: %(key)s",
                        line=index,
                        key=line,
                    )
                )
            keys[entry.key.get_name()] = entry.key
        return keys

    def sftp_connection(self):
        """Return an SFTP connection with the record's host key policy."""
        self.ensure_one()
        _logger.debug(
            "Trying to connect to sftp://%s@%s:%d",
            self.sftp_user,
            self.sftp_host,
            self.sftp_port,
        )
        return _SftpClient(self)
