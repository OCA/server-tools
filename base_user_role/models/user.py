# -*- coding: utf-8 -*-
# Copyright 2014 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    role_line_ids = fields.One2many(
        'res.users.role.line', 'user_id', string=u"Role lines")
    role_ids = fields.One2many(
        'res.users.role', string=u"Roles", compute='_compute_role_ids')

    @api.multi
    @api.depends('role_line_ids.role_id')
    def _compute_role_ids(self):
        for user in self:
            user.role_ids = user.role_line_ids.mapped('role_id')

    @api.model
    def create(self, vals):
        new_record = super(ResUsers, self).create(vals)
        new_record.set_groups_from_roles()
        return new_record

    @api.multi
    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        self.sudo().set_groups_from_roles()
        return res

    @api.multi
    def set_groups_from_roles(self):
        """Set (replace) the groups following the roles defined on users.
        If no role is defined on the user, its groups are let untouched.
        """
        for user in self:
            if not user.role_line_ids:
                continue
            group_ids = []
            role_lines = user.role_line_ids.filtered(
                lambda rec: rec.is_enabled)
            for role_line in role_lines:
                role = role_line.role_id
                group_ids.append(role.group_id.id)
                group_ids.extend(role.implied_ids.ids)
            group_ids = list(set(group_ids))    # Remove duplicates IDs
            vals = {
                'groups_id': [(6, 0, group_ids)],
            }
            super(ResUsers, user).write(vals)
        return True
