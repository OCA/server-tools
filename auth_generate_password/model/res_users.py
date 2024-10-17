import random
import string  # flake8: noqa

from odoo import _, api, exceptions, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    password_sent = fields.Boolean(default=False)

    def generate_set_and_send_password(self):
        icp_obj = self.env["ir.config_parameter"]
        try:
            password_size = int(
                icp_obj.get_param("auth_generate_password.password_size")
            )
        except Exception:
            raise exceptions.UserError(_("error"), _("Only digit chars authorized"))
        password_chars = string.ascii_letters + string.digits
        email_template = self.env.ref(
            "auth_generate_password.generate_password_template"
        )

        for user in self:
            if not user.email:
                # no email user is allowed in odoo14, obviously no email can be sent.
                return True
            # Generate Password
            password = "".join(
                [random.choice(password_chars) for n in range(password_size)]
            )
            # inverse function will call set_password
            user.password = password
            # Send Mail
            mail_id = email_template.with_context(
                generated_password=password
            ).send_mail(
                user.id,
                force_send=True,
                raise_exception=False,
                notif_layout=False,
            )
            if mail_id:
                user.password_sent = True
        return mail_id

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        for user in users:
            user.generate_set_and_send_password()
        return users

    def write(self, values):
        users_no_email = self.filtered(lambda u: not u.email and not u.password_sent)
        res = super(ResUsers, self).write(values)
        if "email" in values and users_no_email:
            # user had no email and receives email for the first time, make pwd and send.
            # the password_sent boolean ensures password is sent once, even if user has
            # email removed and changed multiple times.
            users_no_email.generate_set_and_send_password()
        return res
