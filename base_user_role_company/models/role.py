# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResUsersRoleLine(models.Model):
    _inherit = "res.users.role.line"

    company_id = fields.Many2one(
        "res.company",
        "Company",
        help="If set, this role only applies when this is the main company selected."
        " Otherwise it applies to all companies.",
    )
    active_role = fields.Boolean(string="Active Role", default=True)

    @api.constrains("user_id", "company_id")
    def _check_company(self):
        for record in self:
            if (
                record.company_id
                and record.company_id != record.user_id.company_id
                and record.company_id not in record.user_id.company_ids
            ):
                raise ValidationError(
                    _('User "{}" does not have access to the company "{}"').format(
                        record.user_id.name, record.company_id.name
                    )
                )

    _sql_constraints = [
        (
            "user_role_uniq",
            "unique (user_id,role_id,company_id)",
            "Roles can be assigned to a user only once at a time",
        )
    ]


class ResUsers(models.Model):
    _inherit = "res.users"

    def _get_enabled_roles(self):
        res = super()._get_enabled_roles()
        return res.filtered("active_role")

    @api.model
    def _set_session_active_roles(self, cids):
        """
        Based on the selected companies (cids),
        calculate the roles to enable.
        A role should be enabled only when it applies to all selected companies.
        """
        for role_line in self.env.user.role_line_ids:
            if not role_line.company_id:
                role_line.active_role = True
            elif role_line.company_id.id in cids:
                is_on_companies = self.env.user.role_line_ids.filtered(
                    lambda x: x.role_id == role_line.role_id and x.company_id.id in cids
                )
                role_line.active_role = len(is_on_companies) == len(cids)
            else:
                role_line.active_role = False
