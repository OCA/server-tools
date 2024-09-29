# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    last_role_line_modification = fields.Datetime(
        string="Last roles modification",
        readonly=True,
    )

    @api.model
    def _prepare_role_line_history_dict(self, role_line):
        return {
            'user_id': role_line.user_id.id,
            'role_id': role_line.role_id.id,
            'date_from': fields.Date.from_string(role_line.date_from),
            'date_to': fields.Date.from_string(role_line.date_to),
            'is_enabled': role_line.is_enabled,
        }

    @api.multi
    def _get_role_line_values_by_user(self):
        role_line_values_by_user = {}
        for rec in self:
            role_line_values_by_user.setdefault(rec, {})
            for role_line in rec.role_line_ids:
                role_line_values_by_user[rec][role_line.id] = \
                    self._prepare_role_line_history_dict(role_line)
        return role_line_values_by_user

    @api.model
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        if 'role_line_ids' not in vals:
            return res
        new_role_line_values_by_user = res._get_role_line_values_by_user()
        self.env['base.user.role.line.history'].create_from_vals(
            {},
            new_role_line_values_by_user
        )
        res.last_role_line_modification = fields.Datetime.now()
        return res

    @api.multi
    def write(self, vals):
        if 'role_line_ids' not in vals:
            return super(ResUsers, self).write(vals)
        old_role_line_values_by_user = self._get_role_line_values_by_user()
        res = super(ResUsers, self).write(vals)
        new_role_line_values_by_user = self._get_role_line_values_by_user()
        self.env['base.user.role.line.history'].create_from_vals(
            old_role_line_values_by_user,
            new_role_line_values_by_user
        )
        self.write({
            'last_role_line_modification': fields.Datetime.now()
        })
        return res

    @api.multi
    def show_role_lines_history(self):  # pragma: no cover
        self.ensure_one()
        domain = [('user_id', '=', self.id)]
        return {
            'name': _("Roles history"),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'base.user.role.line.history',
            'domain': domain,
        }
