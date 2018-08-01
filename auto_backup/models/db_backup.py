# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2015 Agile Business Group <http://www.agilebg.com>
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
import shutil
import traceback
from contextlib import contextmanager
from datetime import datetime, timedelta
from glob import iglob

from odoo import _, api, exceptions, fields, models, tools
from odoo.service import db

_logger = logging.getLogger(__name__)
try:
    import pysftp
except ImportError:  # pragma: no cover
    _logger.debug('Cannot import pysftp')


class DbBackup(models.Model):
    _description = 'Database Backup'
    _name = 'db.backup'
    _inherit = "mail.thread"

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "Cannot duplicate a configuration."),
        ("days_to_keep_positive", "CHECK(days_to_keep >= 0)",
         "I cannot remove backups from the future. Ask Doc for that."),
    ]

    name = fields.Char(
        compute="_compute_name",
        store=True,
        help="Summary of this backup process",
    )
    folder = fields.Char(
        default=lambda self: self._default_folder(),
        help='Absolute path for storing the backups',
        required=True
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
        'SFTP Server',
        help=(
            "The host name or IP address from your remote"
            " server. For example 192.168.0.1"
        )
    )
    sftp_port = fields.Integer(
        "SFTP Port",
        default=22,
        help="The port on the FTP server that accepts SSH/SFTP calls."
    )
    sftp_user = fields.Char(
        'Username in the SFTP Server',
        help=(
            "The username where the SFTP connection "
            "should be made with. This is the user on the external server."
        )
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

    backup_format = fields.Selection(
        [("zip", "zip (includes filestore)"), ("dump", "pg_dump custom format (without filestore)")],
        default='zip',
        help="Choose the format for this backup."
    )

    @api.model
    def _default_folder(self):
        """Default to ``backups`` folder inside current server datadir."""
        return os.path.join(
            tools.config["data_dir"],
            "backups",
            self.env.cr.dbname)

    @api.multi
    @api.depends("folder", "method", "sftp_host", "sftp_port", "sftp_user")
    def _compute_name(self):
        """Get the right summary for this job."""
        for rec in self:
            if rec.method == "local":
                rec.name = "%s @ localhost" % rec.folder
            elif rec.method == "sftp":
                rec.name = "sftp://%s@%s:%d%s" % (
                    rec.sftp_user, rec.sftp_host, rec.sftp_port, rec.folder)

    @api.multi
    @api.constrains("folder", "method")
    def _check_folder(self):
        """Do not use the filestore or you will backup your backups."""
        for record in self:
            if (record.method == "local" and
                    record.folder.startswith(
                        tools.config.filestore(self.env.cr.dbname))):
                raise exceptions.ValidationError(
                    _("Do not save backups on your filestore, or you will "
                      "backup your backups too!"))

    @api.multi
    def action_sftp_test_connection(self):
        """Check if the SFTP settings are correct."""
        try:
            # Just open and close the connection
            with self.sftp_connection():
                raise exceptions.Warning(_("Connection Test Succeeded!"))
        except (pysftp.CredentialException,
                pysftp.ConnectionException,
                pysftp.SSHException):
            _logger.info("Connection Test Failed!", exc_info=True)
            raise exceptions.Warning(_("Connection Test Failed!"))

    @api.multi
    def action_backup(self):
        """Run selected backups."""
        backup = None
        filename = self.filename(datetime.now())
        successful = self.browse()

        # Start with local storage
        for rec in self.filtered(lambda r: r.method == "local"):
            with rec.backup_log():
                # Directory must exist
                try:
                    os.makedirs(rec.folder)
                except OSError:
                    pass

                with open(os.path.join(rec.folder, filename),
                          'wb') as destiny:
                    # Copy the cached backup
                    if backup:
                        with open(backup) as cached:
                            shutil.copyfileobj(cached, destiny)
                    # Generate new backup
                    else:
                        db.dump_db(self.env.cr.dbname, destiny, backup_format=rec.backup_format)
                        backup = backup or destiny.name
                successful |= rec

        # Ensure a local backup exists if we are going to write it remotely
        sftp = self.filtered(lambda r: r.method == "sftp")
        if sftp:
            for rec in sftp:
                with rec.backup_log():

                    if backup:
                        cached = open(backup)
                    else:
                        cached = db.dump_db(self.env.cr.dbname, None, backup_format=rec.backup_format)

                    with cached:
                        with rec.sftp_connection() as remote:
                            # Directory must exist
                            try:
                                remote.makedirs(rec.folder)
                            except pysftp.ConnectionException:
                                pass

                            # Copy cached backup to remote server
                            with remote.open(
                                    os.path.join(rec.folder, filename),
                                    "wb") as destiny:
                                shutil.copyfileobj(cached, destiny)
                        successful |= rec

        # Remove old files for successful backups
        successful.cleanup()

    @api.model
    def action_backup_all(self):
        """Run all scheduled backups."""
        return self.search([]).action_backup()

    @api.multi
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
                "<p>%s</p><pre>%s</pre>" % (
                    _("Database backup failed."),
                    escaped_tb),
                subtype=self.env.ref(
                    "auto_backup.mail_message_subtype_failure"
                ),
            )
        else:
            _logger.info("Database backup succeeded: %s", self.name)
            self.message_post(_("Database backup succeeded."))

    @api.multi
    def cleanup(self):
        """Clean up old backups."""
        now = datetime.now()
        for rec in self.filtered("days_to_keep"):
            with rec.cleanup_log():
                oldest = self.filename(now - timedelta(days=rec.days_to_keep))

                if rec.method == "local":
                    for name in iglob(os.path.join(rec.folder,
                                                   "*.dump.zip")):
                        if os.path.basename(name) < oldest:
                            os.unlink(name)

                elif rec.method == "sftp":
                    with rec.sftp_connection() as remote:
                        for name in remote.listdir(rec.folder):
                            if (name.endswith(".dump.zip") and
                                    os.path.basename(name) < oldest):
                                remote.unlink('%s/%s' % (rec.folder, name))

    @api.multi
    @contextmanager
    def cleanup_log(self):
        """Log a possible cleanup failure."""
        self.ensure_one()
        try:
            _logger.info(
                "Starting cleanup process after database backup: %s",
                self.name)
            yield
        except Exception:
            _logger.exception("Cleanup of old database backups failed: %s")
            escaped_tb = tools.html_escape(traceback.format_exc())
            self.message_post(  # pylint: disable=translation-required
                "<p>%s</p><pre>%s</pre>" % (
                    _("Cleanup of old database backups failed."),
                    escaped_tb),
                subtype=self.env.ref("auto_backup.failure"))
        else:
            _logger.info(
                "Cleanup of old database backups succeeded: %s",
                self.name)

    @staticmethod
    def filename(when):
        """Generate a file name for a backup.

        :param datetime.datetime when:
            Use this datetime instead of :meth:`datetime.datetime.now`.
        """
        return "{:%Y_%m_%d_%H_%M_%S}.dump.zip".format(when)

    @api.multi
    def sftp_connection(self):
        """Return a new SFTP connection with found parameters."""
        self.ensure_one()
        params = {
            "host": self.sftp_host,
            "username": self.sftp_user,
            "port": self.sftp_port,
        }
        _logger.debug(
            "Trying to connect to sftp://%(username)s@%(host)s:%(port)d",
            extra=params)
        if self.sftp_private_key:
            params["private_key"] = self.sftp_private_key
            if self.sftp_password:
                params["private_key_pass"] = self.sftp_password
        else:
            params["password"] = self.sftp_password

        return pysftp.Connection(**params)
