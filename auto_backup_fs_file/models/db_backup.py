# Copyright 2025 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.service import db

from odoo.addons.fs_file.fields import FSFileValue


class DbBackup(models.Model):
    _inherit = "db.backup"

    method = fields.Selection(
        selection_add=[("fs_file", "Fs File")], ondelete={"fs_file": "cascade"}
    )

    fs_file_backup_ids = fields.One2many(
        comodel_name="db.backup.fs.file",
        inverse_name="db_backup_id",
        string="Fs File Backups",
    )

    fs_file_backup_count = fields.Integer(compute="_compute_fs_file_backup_count")

    responsible_id = fields.Many2one("res.users", help="User to be notified.")

    @api.model
    def _get_fs_storage(self):
        """Get the fs_storage to be used for fs_file backups."""
        DbBackupFsFile = self.env["db.backup.fs.file"]
        return DbBackupFsFile.fs_storage()

    def _compute_name(self):
        res = super()._compute_name()
        for record in self.filtered(lambda r: r.method == "fs_file"):
            record.name = _("Fs File Backup - %s", record._get_fs_storage().name)
        return res

    @api.depends("fs_file_backup_ids")
    def _compute_fs_file_backup_count(self):
        """Compute the count of fs_file backups."""
        for record in self:
            record.fs_file_backup_count = len(record.fs_file_backup_ids)

    @api.constrains("method")
    def _check_fs_file_backup_storage(self):
        """Ensure that fs_file method has a storage configured."""
        for record in self.filtered(lambda r: r.method == "fs_file"):
            if not record._get_fs_storage():
                raise ValidationError(
                    _(
                        "You must configure a FS Storage for the "
                        "'%(model_description)s' model - or 'Backup File' - field"
                        " to use the 'Fs File'"
                        " backup method.",
                        model_description=self.fs_file_backup_ids._description,
                    )
                )

    def action_backup(self):
        """Override the action_backup method to add the fs_file method."""
        fs_backups = self.filtered(lambda it: it.method == "fs_file")
        dbname = self.env.cr.dbname
        for fs_backup in fs_backups:
            with fs_backup.backup_log():
                filename = self.filename(
                    fields.Datetime.now(), ext=fs_backup.backup_format
                )
                backup = self.env["db.backup.fs.file"].create(
                    {
                        "name": filename,
                        "db_backup_id": fs_backup.id,
                        "backup_file": FSFileValue(
                            name=filename,
                            value=b"init file",
                        ),
                    }
                )
                with backup.backup_file.open("wb", new_version=False) as f:
                    db.dump_db(dbname, f, fs_backup.backup_format)
                    user_to_notify = fs_backup.responsible_id or self.env.user
                    file_metadata = backup.read(["backup_file"])[0].get("backup_file")
                    base_url = (
                        self.env["ir.config_parameter"].sudo().get_param("web.base.url")
                    )
                    activity_note = Markup(
                        _(
                            "The database backup '%(backup_name)s' is ready."
                            " You can download it from the attachment link: "
                            "<a href='%(download_link)s' target='_blank'>"
                            "%(download_link)s</a>",
                            backup_name=backup.name,
                            download_link=f"{base_url}{file_metadata.get('url')}",
                        )
                    )
                    backup.activity_schedule(
                        "auto_backup_fs_file.mail_act_download_backup",
                        date_deadline=fields.Date.today(),
                        note=activity_note,
                        summary=_("Database backup is ready to download."),
                        user_id=user_to_notify.id,
                    )
        res = super().action_backup()
        return res

    def action_open_fs_backups_view(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "auto_backup_fs_file.db_backup_fs_file_act_window"
        )
        action["domain"] = [("db_backup_id", "=", self.id)]
        return action

    def cleanup(self):
        """Extend cleanup to fs_file backups."""
        for db_backup_conf in self.filtered(
            lambda record: record.method == "fs_file" and record.days_to_keep
        ):
            with db_backup_conf.cleanup_log():
                to_delete = db_backup_conf.fs_file_backup_ids.filtered("is_expired")
                for backup in to_delete:
                    self._get_fs_storage().fs.rm_file(backup.get_fs_storage_filename())
                to_delete.unlink()
        res = super().cleanup()
        return res
