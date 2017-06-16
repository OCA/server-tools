# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

from .ir_config_parameter import THRESHOLD_HIDE
from .res_groups import THRESHOLD_MANAGER


class ResCompany(models.Model):
    _inherit = 'res.company'

    max_users = fields.Integer(
        'Maximum Number of users allowed for this company',
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """ Hide Max User Field when the env var to hide the field is set """
        res = super(ResCompany, self).fields_view_get(
            view_id, view_type, toolbar, submenu
        )
        if THRESHOLD_HIDE:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='max_users']"):
                node.getparent().remove(node)
            res['arch'] = etree.tostring(doc, pretty_print=True)
        return res

    @api.multi
    def write(self, vals):
        """
        Override to disallow manipulation of the user threshold parameter
        when the user does not have the right access
        """
        is_manager = self.env.user.has_group(THRESHOLD_MANAGER)
        if vals.get('max_users') and not is_manager:
            raise AccessError(_(
                'You must be a member of the `User Threshold Manager` to set '
                'this parameter'
            ))
        return super(ResCompany, self).write(vals)
