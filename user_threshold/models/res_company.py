# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

from .ir_config_parameter import HIDE_THRESHOLD


class ResCompany(models.Model):
    _inherit = 'res.company'

    max_users = fields.Integer(
        'Maximum Number of users allowed for this company',
    )

    def _can_manipulate_th(self):
        """ Check to see if the user is a member of the correct group
         Returns:
             True when the user is a member of the threshold manager group
        """
        return self.env.user.has_group(
            'user_threshold.group_threshold_manager'
        )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """ Hide Max User Field when the env var to hide the field is set """
        res = super(ResCompany, self).fields_view_get(
            view_id, view_type, toolbar, submenu
        )
        if HIDE_THRESHOLD:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='max_users']"):
                node.getparent().remove(node)
            res['arch'] = etree.tostring(doc, pretty_print=True)
        return res

    @api.multi
    def write(self, vals):
        """ Override to disallow manipulation of the user threshold parameter
        when the user does not have the right access
        """
        if not self._can_manipulate_th() and vals.get('max_users'):
            raise AccessError(
                _('You do not have access to set this parameter')
            )
        return super(ResCompany, self).write(vals)
