# Copyright 2025 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.fs_file import fields as fs_fields


class DbBackupFsFile(models.Model):
    _name = "db.backup.fs.file"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Database Backup Files"

    name = fields.Char("Backup Filename", required=True)
    db_backup_id = fields.Many2one("db.backup", string="DB Backup", required=True)
    backup_file = fs_fields.FSFile(
        required=False,
        help="The file that contains the database backup",
    )
    is_expired = fields.Boolean(
        compute="_compute_is_expired",
        help="Indicates whether the backup has exceeded its storage time.",
    )

    def _compute_is_expired(self):
        """Compute whether the backup has exceeded its storage time."""
        for record in self:
            days_to_keep = record.db_backup_id.days_to_keep
            if days_to_keep:
                expiration_date = fields.Datetime.add(
                    record.create_date, days=days_to_keep
                )
                record.is_expired = fields.Datetime.now() > expiration_date
            else:
                record.is_expired = False

    @api.model
    def fs_storage(self):
        FsStorage = self.env["fs.storage"]
        fs_storages = FsStorage.search([])
        fs_storage = fs_storages.filtered(
            lambda item: item.field_xmlids
            and "auto_backup_fs_file.field_db_backup_fs_file__backup_file"
            in item.field_xmlids
        )
        if not fs_storage:
            fs_storage = fs_storages.filtered(
                lambda item: item.model_xmlids
                and "auto_backup_fs_file.model_db_backup_fs_file" in item.model_xmlids
            )
        if fs_storage:
            return fs_storage
        return False

    def get_fs_storage_filename(self):
        self.ensure_one()
        return self.backup_file.attachment.store_fname.split("://")[-1]
