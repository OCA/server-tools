# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FsStorage(models.Model):
    _inherit = "fs.storage"

    synchronize_task_ids = fields.One2many(
        "attachment.synchronize.task", "backend_id", string="Tasks"
    )
    import_task_count = fields.Integer(
        "Import Tasks", compute="_compute_import_task_count"
    )
    export_task_count = fields.Integer(
        "Export Tasks", compute="_compute_export_task_count"
    )

    def _compute_import_task_count(self):
        for rec in self:
            rec.import_task_count = len(
                rec.synchronize_task_ids.filtered(lambda t: t.method_type == "import")
            )

    def _compute_export_task_count(self):
        for rec in self:
            rec.export_task_count = len(
                rec.synchronize_task_ids.filtered(lambda t: t.method_type == "export")
            )

    def action_related_import_task(self):
        self.ensure_one()

        act_window_xml_id = "attachment_synchronize.action_attachment_import_task"
        act_window = self.env["ir.actions.act_window"]._for_xml_id(act_window_xml_id)
        domain = [
            ("id", "in", self.synchronize_task_ids.ids),
            ("method_type", "=", "import"),
        ]
        act_window["domain"] = domain
        if self.import_task_count == 1:
            form = self.env.ref("attachment_synchronize.view_attachment_task_form")
            act_window["views"] = [(form.id, "form")]
            act_window["res_id"] = (
                self.env["attachment.synchronize.task"].search(domain).id
            )

        return act_window

    def action_related_export_task(self):
        self.ensure_one()

        act_window_xml_id = "attachment_synchronize.action_attachment_export_task"
        act_window = self.env["ir.actions.act_window"]._for_xml_id(act_window_xml_id)
        domain = [
            ("id", "in", self.synchronize_task_ids.ids),
            ("method_type", "=", "export"),
        ]
        act_window["domain"] = domain
        if self.export_task_count == 1:
            form = self.env.ref("attachment_synchronize.view_attachment_task_form")
            act_window["views"] = [(form.id, "form")]
            act_window["res_id"] = (
                self.env["attachment.synchronize.task"].search(domain).id
            )

        return act_window
