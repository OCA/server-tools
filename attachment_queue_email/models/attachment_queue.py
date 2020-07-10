# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import base64


class AttachmentQueue(models.Model):
    _inherit = "attachment.queue"

    fetchmail_attachment_condition_id = fields.Many2one(
        "fetchmail.attachment.condition",
        string="FetchMail condition",
        help="The Fetchmail attachment condition used to create this attachment",
    )
    fetchmail_server_id = fields.Many2one(
        "fetchmail.server",
        string="Email Server",
        related="fetchmail_attachment_condition_id.server_id",
        store=True,
        readonly=True,
        help="The email server used to create this attachment",
    )

    @api.model
    def _get_attachment_queue_data(self, condition, msg, att):
        values = {
            "fetchmail_attachment_condition_id": condition.id,
            "file_type": condition.file_type,
            "name": msg["subject"],
            "sync_date": msg["date"],
            "datas_fname": att[0],
            "datas": base64.b64encode(att[1]),
            "state": "pending",
        }
        return values

    @api.model
    def prepare_data_from_basic_condition(self, condition, msg):
        vals_list = []
        if (
            condition.from_email in msg["from"]
            and condition.mail_subject in msg["subject"]
        ):
            for att in msg["attachments"]:
                if condition.file_extension in att[0] or not condition.file_extension:
                    vals_list.append(
                        self._get_attachment_queue_data(condition, msg, att)
                    )
        return vals_list

    @api.model
    def _prepare_data_for_attachment_queue(self, msg):
        """Prepare the datas for the creation of one or many attachment.queue depending
        on the number of the email's attachments files and if the email matches the
        fetchmail.attachment.condition's conditions.

        :param msg: a dictionnary with the email data
        :type: dict

        :return: a list of dictionnary that contains the attachment.queue data
        :rtype: list
        """
        res = []
        server_id = self.env.context.get("default_fetchmail_server_id", False)
        file_condition_obj = self.env["fetchmail.attachment.condition"]
        conds = file_condition_obj.search([("server_id", "=", server_id)])
        for cond in conds:
            vals_list = self.prepare_data_from_basic_condition(cond, msg)
            if vals_list:
                res += vals_list
        return res

    @api.model
    def message_new(self, msg, custom_values):
        """Create Attachments Queues objects from the new received email's attachments.
        """
        # Rewriting completely ``message_new`` instead of overiding it in order to
        # allows the creation of many new objects instead of only one.
        created_recs = []
        res = self._prepare_data_for_attachment_queue(msg)
        if res:
            for vals in res:
                default = self.env.context.get("default_attachment_queue_vals")
                if default:
                    for key in default:
                        if key not in vals:
                            vals[key] = default[key]
                created_recs.append(self.create(vals))
            return created_recs[0]
        return None
