# Copyright 2026 Cetmix
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

REASON_MISSING_FILE = "missing_file"
ATTACHMENT_FIND_BATCH = 5000


class CleanupPurgeLineAttachment(models.TransientModel):
    _inherit = "cleanup.purge.line"
    _name = "cleanup.purge.line.attachment"
    _description = "Cleanup Purge Line Attachment"

    attachment_id = fields.Many2one("ir.attachment")
    reason = fields.Selection(
        [
            (REASON_MISSING_FILE, "File missing in filestore"),
        ],
    )
    error_message = fields.Char(readonly=True)
    wizard_id = fields.Many2one("cleanup.purge.wizard.attachment", readonly=True)

    def purge(self):
        """Unlink orphaned attachment records upon manual confirmation.

        Filters unpurged lines with attachment_id. Unlinks each attachment
        individually; failures are logged and skipped so the batch continues.
        Only successfully removed attachments get their lines marked purged.

        :return: result of write({"purged": True}) on successfully purged lines,
            or True if none were purged
        """
        if self:
            objs = self
        else:
            objs = self.env["cleanup.purge.line.attachment"].browse(
                self._context.get("active_ids")
            )
        to_unlink = objs.filtered(lambda x: not x.purged and x.attachment_id)
        self.logger.info("Purging attachments: %s", to_unlink.mapped("name"))
        purged_line_ids = []
        for line in to_unlink:
            attach = line.attachment_id
            try:
                attach.unlink()
                purged_line_ids.append(line.id)
            except (UserError, ValidationError, AccessError) as exc:
                self.logger.warning(
                    "Attachment #%s cannot be deleted: %s",
                    attach.id,
                    str(exc),
                )
                line.error_message = str(exc)
        if not purged_line_ids:
            return True
        return (
            self.env["cleanup.purge.line.attachment"]
            .browse(purged_line_ids)
            .write({"purged": True})
        )


class CleanupPurgeWizardAttachment(models.TransientModel):
    _inherit = "cleanup.purge.wizard"
    _name = "cleanup.purge.wizard.attachment"
    _description = "Purge attachments"

    @api.model
    def find(self):
        """Collect ir.attachment records whose backing files are missing on disk.

        Requires file storage. Searches binary attachments with store_fname,
        checks each file exists via os.path.isfile(_full_path(store_fname)).

        :raises UserError: if storage != "file" or no orphaned entries found
        """
        if self.env["ir.attachment"]._storage() != "file":
            raise UserError(
                _(
                    "Attachment storage is not 'file'. "
                    "Purge of orphaned attachments only works with file storage."
                )
            )
        res = []
        last_id = 0
        ir_attachment = self.env["ir.attachment"]
        while True:
            rows = ir_attachment.search_read(
                [
                    ("id", ">", last_id),
                    ("store_fname", "!=", False),
                    ("type", "=", "binary"),
                ],
                ["store_fname", "name"],
                limit=ATTACHMENT_FIND_BATCH,
                order="id",
            )
            if not rows:
                break
            batch_ids = [row["id"] for row in rows]
            last_id = batch_ids[-1]
            for row in rows:
                full_path = ir_attachment._full_path(row["store_fname"])
                if not os.path.isfile(full_path):
                    res.append(
                        fields.Command.create(
                            {
                                "attachment_id": row["id"],
                                "name": row["store_fname"]
                                or row["name"]
                                or str(row["id"]),
                                "reason": REASON_MISSING_FILE,
                            }
                        )
                    )
            ir_attachment.browse(batch_ids).invalidate_recordset(
                ["store_fname", "name"]
            )
        if not res:
            raise UserError(_("No orphaned attachment entries found"))
        return res

    purge_line_ids = fields.One2many("cleanup.purge.line.attachment", "wizard_id")
