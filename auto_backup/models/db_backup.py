# -*- coding: utf-8 -*-
# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2015 Agile Business Group <http://www.agilebg.com>
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

import shutil
import traceback
from contextlib import contextmanager
from datetime import datetime, timedelta
from glob import iglob
from odoo import exceptions, models, fields, api, _, tools
from odoo.service import db
import logging
_logger = logging.getLogger(__name__)


class DbBackup(models.Model):
    _name = 'db.backup'
    _inherit = "mail.thread"

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "Cannot duplicate a configuration."),
        ("days_to_keep_positive", "CHECK(days_to_keep >= 0)",
         "I cannot remove backups from the future. Ask Doc for that."),
    ]

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
        help='Summary of this backup process',
    )
    system_id = fields.Many2one(
        string='External System',
        comodel_name='external.system',
        required=True,
    )
    folder = fields.Char(
        default=lambda self: self._default_folder(),
        oldname='bkp_dir',
        help='Absolute path for storing the backups',
        compute='_compute_folder',
        inverse='_inverse_folder',
        required=True,
    )
    _folder = fields.Char(
        help='Path, relative to the external system root, to store the '
             'backup.',
    )
    days_to_keep = fields.Integer(
        oldname='daystokeep',
        required=True,
        default=0,
        help='Backups older than this will be deleted automatically. '
             'Set 0 to disable autodeletion.',
    )
    sftp_host = fields.Char(
        string='SFTP Server',
        oldname="sftpip",
        related='system_id.host',
        help=(
            "The host name or IP address from your remote"
            " server. For example 192.168.0.1"
        )
    )
    sftp_port = fields.Integer(
        string="SFTP Port",
        default=22,
        oldname="sftpport",
        related='system_id.port',
        help="The port on the FTP server that accepts SSH/SFTP calls."
    )
    sftp_user = fields.Char(
        string='Username in the SFTP Server',
        oldname="sftpusername",
        related='system_id.username',
        help=(
            "The username where the SFTP connection "
            "should be made with. This is the user on the external server."
        )
    )
    sftp_password = fields.Char(
        string="SFTP Password",
        oldname="sftppassword",
        related='system_id.password',
        help="The password for the SFTP connection. If you specify a private "
             "key file, then this is the password to decrypt it.",
    )
    sftp_private_key = fields.Char(
        string="Private key location",
        related='system_id.private_key',
        help="Path to the private key file. Only the Odoo user should have "
             "read permissions for that file.",
    )
    method = fields.Selection(
        related='system_id.system_type',
        default='external.system.os',
        help='Choose the storage method for this backup.',
    )

    @api.model
    def _default_folder(self):
        """Default to ``backups`` folder inside current server datadir."""
        return os.path.join(
            tools.config['data_dir'],
            'backups',
            self.env.cr.dbname,
        )

    @api.multi
    @api.depends('folder', 'system_id.name')
    def _compute_name(self):
        """Get the right summary for this job."""
        for record in self:
            record.name = '%s/%s' % (
                record.system_id.name, record.folder,
            )

    @api.multi
    @api.depends('_folder', 'system_id.remote_folder')
    def _compute_folder(self):
        for record in self:
            record.folder = '%s/%s' % (
                record.system_id.remote_folder, record._folder,
            )

    @api.multi
    def _inverse_folder(self):
        for record in self:
            record._folder = record.folder.replace(
                '%s/' % record.system_id.remote_folder, '',
            )

    @api.multi
    @api.constrains("folder", "method")
    def _check_folder(self):
        """Do not use the filestore or you will backup your backups."""
        for s in self:
            if (s.method == "external.system.os" and
                    s.folder.startswith(
                        tools.config.filestore(self.env.cr.dbname))):
                raise exceptions.ValidationError(
                    _("Do not save backups on your filestore, or you will "
                      "backup your backups too!"))

    @api.multi
    def action_sftp_test_connection(self):
        """Check if the SFTP settings are correct."""
        self.ensure_one()
        self.system_id.action_test_connection()

    @api.multi
    def action_backup(self):
        """Run selected backups."""
        backup = None
        filename = self.filename(datetime.now())
        successful = self.browse()
        local, external = self.browse()

        for record in self:
            if record.method == 'external.system.os':
                local |= record
            else:
                external |= record

        # Start with local storage
        for record in local:
            with record.backup_log():
                with record.system_id.client() as os:
                    # Directory must exist
                    try:
                        os.makedirs(record.folder)
                    except OSError:
                        pass

                with os.open(filename, 'wb') as destiny:
                    # Copy the cached backup
                    if backup:
                        with open(backup) as cached:
                            shutil.copyfileobj(cached, destiny)
                    # Generate new backup
                    else:
                        db.dump_db(self.env.cr.dbname, destiny)
                        backup = backup or destiny.name
                successful |= record

        # Ensure a local backup exists if we are going to write it remotely
        if external:
            if backup:
                cached = open(backup)
            else:
                cached = db.dump_db(self.env.cr.dbname, None)

            with cached:
                for record in external:
                    with record.backup_log():
                        with record.system_id.client() as remote:
                            # Directory must exist
                            try:
                                remote.mkdir(record._folder)
                            except Exception:
                                pass

                            # Copy cached backup to remote server
                            with remote.open(filename, "wb") as destiny:
                                shutil.copyfileobj(cached, destiny)
                        successful |= record

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
        except:
            _logger.exception("Database backup failed: %s", self.name)
            escaped_tb = tools.html_escape(traceback.format_exc())
            self.message_post(
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
        for record in self.filtered("days_to_keep"):
            with record.cleanup_log():
                oldest = self.filename(now - timedelta(days=record.days_to_keep))
                with record.system_id.client() as remote:
                    for name in remote.listdir(record._folder):
                        if (name.endswith(".dump.zip") and
                                os.path.basename(name) < oldest):
                            remote.unlink('%s/%s' % (record._folder, name))

    @api.multi
    @contextmanager
    def cleanup_log(self):
        """Log a possible cleanup failure."""
        self.ensure_one()
        try:
            _logger.info("Starting cleanup process after database backup: %s",
                         self.name)
            yield
        except:
            _logger.exception("Cleanup of old database backups failed: %s")
            escaped_tb = tools.html_escape(traceback.format_exc())
            self.message_post(
                "<p>%s</p><pre>%s</pre>" % (
                    _("Cleanup of old database backups failed."),
                    escaped_tb),
                subtype=self.env.ref("auto_backup.failure"))
        else:
            _logger.info("Cleanup of old database backups succeeded: %s",
                         self.name)

    @api.model
    def filename(self, when):
        """Generate a file name for a backup.

        :param datetime.datetime when:
            Use this datetime instead of :meth:`datetime.datetime.now`.
        """
        return "{:%Y_%m_%d_%H_%M_%S}.dump.zip".format(when)
