# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os
from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError

from .ir_config_parameter import HIDE_THRESHOLD, MAX_DB_USER_PARAM
from .res_groups import THRESHOLD_MANAGER


class ResUsers(models.Model):
    _inherit = 'res.users'

    threshold_exempt = fields.Boolean(
        'Exempt User From User Count Thresholds',
    )

    def __init__(self, pool, cr):
        """ Override to check if env var to hide threshold configuration and
        reset the database state is set. If it is, run those actions
        """
        if HIDE_THRESHOLD:
            exempt_users = os.environ.get(
                'USER_THRESHOLD_USER', ''
            ).split(',')
            cr.execute(
                "SELECT name FROM ir_module_module WHERE "
                "name='user_threshold' AND state='installed'"
            )
            if cr.fetchall():
                query = """ UPDATE res_users SET threshold_exempt='False'
                WHERE share='False'"""
                if exempt_users:
                    query = "%s AND login NOT IN ('%s')" % (
                        query, "','".join(exempt_users)
                    )
                cr.execute(query)

    def _check_thresholds(self):
        """ Check to see if any user thresholds are met
        Returns:
            False when the thresholds aren't met and True when they are
        """
        domain = [
            ('threshold_exempt', '=', False),
            ('share', '=', False),
        ]
        db_users = len(self.env['res.users'].search(domain))
        max_db_users = int(self.env['ir.config_parameter'].get_param(
            MAX_DB_USER_PARAM
        ))
        if max_db_users > 0 and db_users >= max_db_users:
            return True
        company = self.env.user.company_id
        domain.append(('company_id', '=', company.id))
        company_users = len(self.env['res.users'].search(domain))
        if company.max_users > 0 and company_users >= company.max_users:
            return True
        return False

    @api.multi
    def copy(self, default=None):
        """ Override method to make sure the Thresholds aren't met before
        creating a new user
        """
        if self._check_thresholds():
            raise ValidationError(_(
                'Cannot add user - Maximum number of allowed users reached!'
            ))
        return super(ResUsers, self).copy(default=default)

    @api.multi
    def create(self, vals):
        """ Override method to make sure the Thresholds aren't met before
        creating a new user
        """
        if self._check_thresholds():
            raise ValidationError(_(
                'Cannot add user - Maximum number of allowed users reached!'
            ))
        return super(ResUsers, self).create(vals)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """ Hide Max User Field when the env var to hide the field is set """
        res = super(ResUsers, self).fields_view_get(
            view_id, view_type, toolbar, submenu
        )
        if HIDE_THRESHOLD:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//group[@name='user_threshold']"):
                node.getparent().remove(node)
            res['arch'] = etree.tostring(doc, pretty_print=True)
        return res

    @api.multi
    def write(self, vals):
        """ Override write to verify that membership of the Threshold Manager
        group is not able to be set by users outside that group
        """
        th_group = self.env.ref(THRESHOLD_MANAGER)
        user_is_manager = self.env.user.has_group(THRESHOLD_MANAGER)
        if vals.get('threshold_exempt') and not user_is_manager:
            raise AccessError(_(
                'You must be a member of the `User Threshold Manager`'
                ' group to grant threshold exemptions'
            ))
        if vals.get('in_group_%s' % th_group.id) and not user_is_manager:
            raise AccessError(_(
                'You must be a member of the `User Threshold Manager`'
                ' group to grant access to it'
            ))
        return super(ResUsers, self).write(vals)
