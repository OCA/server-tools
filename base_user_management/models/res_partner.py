from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    signup_token = fields.Char(
        groups="base.group_erp_manager,"
        "base_user_management.group_access_right_security_manage_users"
    )
    signup_type = fields.Char(
        groups="base.group_erp_manager,"
        "base_user_management.group_access_right_security_manage_users"
    )
    signup_expiration = fields.Datetime(
        groups="base.group_erp_manager,"
        "base_user_management.group_access_right_security_manage_users"
    )
