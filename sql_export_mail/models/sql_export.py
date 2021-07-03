# Copyright 2019 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


class SqlExport(models.Model):
    _inherit = "sql.export"

    mail_user_ids = fields.Many2many(
        "res.users",
        "mail_user_sqlquery_rel",
        "sql_id",
        "user_id",
        "User to notify",
        help="Add the users who want to receive the report by e-mail. You "
        "need to link the sql query with a cron to send mail automatically",
    )
    cron_ids = fields.Many2many(
        "ir.cron", "cron_sqlquery_rel", "sql_id", "cron_id", "Crons"
    )
    # We could implement other conditions, that is why it is a selection field
    mail_condition = fields.Selection(
        [("not_empty", "File Not Empty")], default="not_empty"
    )

    def create_cron(self):
        self.ensure_one()
        nextcall = datetime.now() + timedelta(hours=2)
        cron_vals = {
            "active": True,
            "model_id": self.env.ref("sql_export.model_sql_export").id,
            "state": "code",
            "code": "model._run_all_sql_export_for_cron()",
            "name": "SQL Export : %s" % self.name,
            "nextcall": nextcall,
            "doall": False,
            "numbercall": -1,
            "user_id": SUPERUSER_ID,
        }
        cron = self.env["ir.cron"].create(cron_vals)
        # We need to pass cron_id in the cron args because a cron is not
        # aware of itself in the end method and we need it to find all
        # linked sql exports
        write_vals = {"code": "model._run_all_sql_export_for_cron([%s])" % cron.id}
        cron.write(write_vals)
        self.write({"cron_ids": [(4, cron.id)]})

    def send_mail(self, params=None):
        self.ensure_one()
        mail_template = self.env.ref("sql_export_mail.sql_export_mailer")
        attach_obj = self.env["ir.attachment"]
        if self.mail_condition == "not_empty":
            res = self._execute_sql_request(params=params, mode="fetchone")
            if not res:
                return
        ctx = self.env.context.copy()
        if params:
            if "user_id" in params:
                ctx["force_user"] = params["user_id"]
            if "company_id" in params:
                ctx["force_company"] = params["company_id"]
        wizard = self.env["sql.file.wizard"].create(
            {
                "sql_export_id": self.id,
            }
        )
        wizard.with_context(ctx).export_sql()
        binary = wizard.binary_file
        filename = wizard.file_name
        msg_id = mail_template.send_mail(self.id, force_send=False)
        mail = self.env["mail.mail"].browse(msg_id)
        attach_vals = {
            "name": filename,
            "datas": binary,
            "res_model": "mail.mail",
            "res_id": mail.id,
        }
        attachment = attach_obj.create(attach_vals)
        mail.write({"attachment_ids": [(4, attachment.id)]})

    @api.model
    def _run_all_sql_export_for_cron(self, cron_ids):
        exports = self.search([("cron_ids", "in", cron_ids)])
        for export in exports:
            if "%(company_id)s" in export.query and "%(user_id)s" not in export.query:
                variable_dict = {}
                companies = self.env["res.company"].search([])
                for company in companies:
                    users = export.mail_user_ids.filtered(
                        lambda u: u.company_id == company
                    )
                    if users:
                        variable_dict["company_id"] = users[0].company_id.id
                        export.with_context(mail_to=users.ids).send_mail(
                            params=variable_dict
                        )
            elif "%(user_id)s" in export.query:
                variable_dict = {}
                for user in export.mail_user_ids:
                    variable_dict["user_id"] = user.id
                    if "%(company_id)s" in export.query:
                        variable_dict["company_id"] = user.company_id.id
                    export.with_context(mail_to=[user.id]).send_mail(
                        params=variable_dict
                    )
            else:
                export.send_mail()

    @api.constrains("field_ids", "mail_user_ids")
    def check_no_parameter_if_sent_by_mail(self):
        for export in self:
            if export.field_ids and export.mail_user_ids:
                raise UserError(
                    _(
                        "It is not possible to execute and send a query "
                        "automatically by mail if there are parameters to fill"
                    )
                )

    @api.constrains("mail_user_ids")
    def check_mail_user(self):
        for export in self:
            for user in export.mail_user_ids:
                if not user.email:
                    raise UserError(_("The user does not have any e-mail address."))

    def get_email_address_for_template(self):
        """
        Called from mail template
        """
        self.ensure_one()
        if self.env.context.get("mail_to"):
            mail_users = self.env["res.users"].browse(self.env.context.get("mail_to"))
        else:
            mail_users = self.mail_user_ids
        return ",".join([x.email for x in mail_users if x.email])
