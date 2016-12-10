# -*- coding: utf-8 -*-
# Copyright 2014 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import logging

from openerp import api, fields, models


_logger = logging.getLogger(__name__)


class ResUsersRole(models.Model):
    _name = 'res.users.role'
    _inherits = {'res.groups': 'group_id'}
    _description = "User role"

    group_id = fields.Many2one(
        'res.groups', required=True, ondelete='cascade',
        readonly=True, string=u"Associated group")
    line_ids = fields.One2many(
        'res.users.role.line', 'role_id', string=u"Users")
    user_ids = fields.One2many(
        'res.users', string=u"Users", compute='_compute_user_ids')

    _defaults = {   # pylint: disable=attribute-deprecated
        'category_id': api.model(
            lambda cls: cls.env.ref(
                'base_user_role.ir_module_category_role').id),
    }

    @api.multi
    @api.depends('line_ids.user_id')
    def _compute_user_ids(self):
        for role in self:
            role.user_ids = role.line_ids.mapped('user_id')

    @api.model
    def create(self, vals):
        new_record = super(ResUsersRole, self).create(vals)
        new_record.update_users()
        return new_record

    @api.multi
    def write(self, vals):
        res = super(ResUsersRole, self).write(vals)
        self.update_users()
        return res

    @api.multi
    def update_users(self):
        """Update all the users concerned by the roles identified by `ids`."""
        users = self.mapped('user_ids')
        users.set_groups_from_roles()
        return True

    @api.model
    def cron_update_users(self):
        logging.info(u"Update user roles")
        self.search([]).update_users()


class ResUsersRoleLine(models.Model):
    _name = 'res.users.role.line'
    _description = 'Users associated to a role'

    role_id = fields.Many2one(
        'res.users.role', string=u"Role", ondelete='cascade')
    user_id = fields.Many2one(
        'res.users', string=u"User")
    date_from = fields.Date(u"From")
    date_to = fields.Date(u"To")
    is_enabled = fields.Boolean(u"Enabled", compute='_compute_is_enabled')

    @api.multi
    @api.depends('date_from', 'date_to')
    def _compute_is_enabled(self):
        today = datetime.date.today()
        for role_line in self:
            role_line.is_enabled = True
            if role_line.date_from:
                date_from = fields.Date.from_string(role_line.date_from)
                if date_from > today:
                    role_line.is_enabled = False
            if role_line.date_to:
                date_to = fields.Date.from_string(role_line.date_to)
                if today > date_to:
                    role_line.is_enabled = False
