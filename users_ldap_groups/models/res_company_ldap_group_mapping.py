# -*- coding: utf-8 -*-
# © 2012-2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResCompanyLdapGroupMapping(models.Model):
    _name = 'res.company.ldap.group_mapping'
    _rec_name = 'ldap_attribute'
    _order = 'ldap_attribute'

    ldap_id = fields.Many2one(
        'res.company.ldap', 'LDAP server', required=True, ondelete='cascade',
    )
    ldap_attribute = fields.Char(
        'LDAP attribute',
        help='The LDAP attribute to check.\n'
             'For active directory, use memberOf.')
    operator = fields.Selection(
        lambda self: [
            (o, o) for o in self.env['res.company.ldap.operator'].operators()
        ],
        'Operator',
        help='The operator to check the attribute against the value\n'
        'For active directory, use \'contains\'', required=True)
    value = fields.Char(
        'Value',
        help='The value to check the attribute against.\n'
        'For active directory, use the dn of the desired group',
        required=True)
    group_id = fields.Many2one(
        'res.groups', 'Odoo group', oldname='group',
        help='The Odoo group to assign', required=True)
