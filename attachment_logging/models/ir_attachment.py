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
            "%(username)s %(action)s a file: %(filename)s",
            username=self.create_uid.name,
            filename=self.name,
            action=action,
        )
        record.message_post(
            body=message_text,
            message_type="notification",
            author_id=self.env.ref("base.user_root").partner_id.id,
            subtype_xmlid="attachment_logging.mt_attachment",
        )

    @api.model
    def _is_use_attachment_log(self):
        """Check use attachment log"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("attachment_logging.use_attachment_log", False)
        )

    def _post_add_create(self, **kwargs):
        result = super()._post_add_create(**kwargs)
        if self._is_use_attachment_log():
            # Send notification after creation attachments
            for attachment in self:
                if self.pool and issubclass(
                    self.pool[attachment.res_model], self.pool["mail.thread"]
                ):
                    attachment._send_attachment_notification(is_create=True)
        return result

    def _delete_and_notify(self, message=None):
        if self._is_use_attachment_log():
            for attachment in self:
                if self.pool and issubclass(
                    self.pool[attachment.res_model], self.pool["mail.thread"]
                ):
                    attachment._send_attachment_notification(is_unlink=True)
        return super()._delete_and_notify(message)

    def _attachment_format(self):
        attachment_vals = super()._attachment_format()
        for attachment_val in attachment_vals:
            attachment = self.browse(attachment_val["id"])
            attachment_val.update(
                {
                    "create_user": attachment.create_uid.name,
                    "create_date": format_datetime(
                        self.env, attachment_val["create_date"]
                    ),
                }
            )
        return attachment_vals
