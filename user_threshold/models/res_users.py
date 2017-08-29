# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os
from csv import reader
from lxml import etree

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import AccessError, ValidationError

from .ir_config_parameter import THRESHOLD_HIDE, MAX_DB_USER_PARAM
from .res_groups import THRESHOLD_MANAGER


class ResUsers(models.Model):
    _inherit = 'res.users'

    threshold_exempt = fields.Boolean(
        'Exempt User From User Count Thresholds',
    )

    def __init__(self, pool, cr):
        """
        Override to check if env var to hide threshold configuration and
        reset the database state is set. If it is, run those actions
        """
        if THRESHOLD_HIDE:
            exempt_users_var = os.environ.get('USER_THRESHOLD_USER', '')
            exempt_users = reader([exempt_users_var])
            with api.Environment.manage():
                env = api.Environment(cr, SUPERUSER_ID, {})
                installed = env['ir.module.module'].search_count([
                    ('name', '=', 'user_threshold'),
                    ('state', '=', 'installed'),
                ])
                if installed:
                    users = env['res.users'].search([
                        ('share', '=', False),
                        ('threshold_exempt', '=', True),
                    ])
                    non_ex = users.filtered(
                        lambda r: r.login not in exempt_users
                    )
                    for user in non_ex:
                        user.threshold_exempt = False

    def _check_thresholds(self):
        """
        Check to see if any user thresholds are met
        Returns:
            False when the thresholds aren't met and True when they are
        """
        domain = [
            ('threshold_exempt', '=', False),
            ('share', '=', False),
        ]
        users = self.env['res.users'].search(domain)
        max_db_users = int(self.env['ir.config_parameter'].get_param(
            MAX_DB_USER_PARAM
        ))
        if max_db_users > 0 and len(users) >= max_db_users:
            return True
        company = self.env.user.company_id
        company_users = users.filtered(lambda r: r.company_id.id == company.id)
        if company.max_users > 0 and len(company_users) >= company.max_users:
            return True
        return False

    @api.multi
    def copy(self, default=None):
        """
        Override method to make sure the Thresholds aren't met before
        creating a new user
        """
        if self._check_thresholds():
            raise ValidationError(_(
                'Cannot add user - Maximum number of allowed users reached'
            ))
        return super(ResUsers, self).copy(default=default)

    @api.multi
    def create(self, vals):
        """
        Override method to make sure the Thresholds aren't met before
        creating a new user
        """
        if self._check_thresholds():
            raise ValidationError(_(
                'Cannot add user - Maximum number of allowed users reached'
            ))
        return super(ResUsers, self).create(vals)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """ Hide Max User Field when the env var to hide the field is set """
        res = super(ResUsers, self).fields_view_get(
            view_id, view_type, toolbar, submenu
        )
        if THRESHOLD_HIDE:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//group[@name='user_threshold']"):
                node.getparent().remove(node)
            res['arch'] = etree.tostring(doc, pretty_print=True)
        return res

    @api.multi
    def write(self, vals):
        """
        Override write to verify that membership of the Threshold Manager
        group is not able to be set by users outside that group
        """
        thold_group = self.env.ref(THRESHOLD_MANAGER, raise_if_not_found=False)
        if thold_group:
            user_is_manager = self.env.user.has_group(THRESHOLD_MANAGER)
            if vals.get('threshold_exempt') and not user_is_manager:
                raise AccessError(_(
                    'You must be a member of the `User Threshold Manager`'
                    ' group to grant threshold exemptions.'
                ))
            is_add_group = vals.get('in_group_%s' % thold_group.id)
            if is_add_group and not user_is_manager:
                raise AccessError(_(
                    'You must be a member of the `User Threshold Manager`'
                    ' group to grant access to it.'
                ))
        return super(ResUsers, self).write(vals)
