from odoo.http import request

from odoo.addons.mail.controllers.discuss import DiscussController


class AttachmentController(DiscussController):
    def mail_attachment_upload(
        self, ufile, thread_id, thread_model, is_pending=False, **kwargs
    ):
        response = super().mail_attachment_upload(
            ufile, thread_id, thread_model, is_pending=is_pending, **kwargs
        )
        attachment_id = response.json.get("id")
        if not attachment_id:
            return response
        # Update attachment data
        attachmentData = {**response.json}
        attachment = request.env["ir.attachment"].sudo().browse(attachment_id).exists()
        if attachment:
            attachmentData.update(**attachment.get_additional_data())
        return request.make_json_response(attachmentData)
