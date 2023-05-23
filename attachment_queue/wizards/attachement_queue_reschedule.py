# Copyright 2013-2020 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class AttachmentQueueReschedule(models.TransientModel):
    _name = "attachment.queue.reschedule"
    _description = "Wizard to reschedule a selection of attachments"

    def _default_attachment_ids(self):
        res = False
        context = self.env.context
        if context.get("active_model") == "attachment.queue" and context.get(
            "active_ids"
        ):
            res = context["active_ids"]
        return res

    attachment_ids = fields.Many2many(
        comodel_name="attachment.queue",
        string="Attachments",
        default=lambda r: r._default_attachment_ids(),
    )

    def reschedule(self):
        attachments = self.attachment_ids
        attachments.button_reschedule()
        return {"type": "ir.actions.act_window_close"}
