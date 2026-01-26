from odoo import _, api, models
from odoo.tools.misc import format_datetime


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _send_attachment_notification(self, is_create=False, is_unlink=False):
        """
        Send attachment notification

        :param is_create: send notification for create method
        :param is_unlink: send notification for unlink method
        """
        if is_create:
            action = _("attached")
        elif is_unlink:
            action = _("unlinked")
        else:
            return
        record = self.env[self.res_model].sudo().browse(self.res_id)
        message_text = _(
            "<b>%(username)s</b> %(action)s a file: <i>%(filename)s</i>",
            username=self.create_uid.name,
            filename=self.name,
            action=action,
        )
        message = record.message_post(
            body=message_text,
            author_id=self.env.ref("base.user_root").partner_id.id,
            subtype_xmlid="attachment_logging.mt_attachment",
        )
        self.env["bus.bus"]._sendone(
            self.env.user.partner_id.id,
            "mail.message/insert",
            {
                "id": message.id,
                "body": message.body,
            },
        )

    @api.model
    def _is_use_attachment_log(self):
        """Check use attachment log"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("attachment_logging.use_attachment_log", False)
        )

    def _post_add_create(self):
        result = super()._post_add_create()
        if not self._is_use_attachment_log():
            return result
        # Send notification after creation attachments
        for attachment in self:
            if self.pool and issubclass(
                self.pool[attachment.res_model], self.pool["mail.thread"]
            ):
                attachment._send_attachment_notification(is_create=True)
        return result

    def _delete_and_notify(self):
        if not self._is_use_attachment_log():
            return super()._delete_and_notify()
        # Send notification before unlink attachments
        for attachment in self:
            if self.pool and issubclass(
                self.pool[attachment.res_model], self.pool["mail.thread"]
            ):
                attachment._send_attachment_notification(is_unlink=True)
        return super()._delete_and_notify()

    def _attachment_format(self, legacy=False):
        res_list = super()._attachment_format(legacy=legacy)
        for res in res_list:
            attachment = self.browse(res.get("id"))
            res.update(**attachment.get_additional_data())
        return res_list

    def get_additional_data(self):
        """Get additional data for attachment"""
        self.ensure_one()
        return {
            "create_date": format_datetime(self.env, self.create_date),
            "create_user": self.create_uid.name,
        }
