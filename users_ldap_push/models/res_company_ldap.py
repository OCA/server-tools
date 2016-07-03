# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import _, models, fields, api, exceptions


class ResCompanyLdap(models.Model):
    _inherit = 'res.company.ldap'

    @api.model
    def _create_ldap_entry_field_mappings_default(self):
        return [
            (0, 0, {
                'field_id':
                self.env.ref('base.field_res_users_login').id,
                'attribute': 'userid',
                'use_for_dn': True,
            }),
        ]

    create_ldap_entry = fields.Boolean('Create ldap entry', default=True)
    create_ldap_entry_base = fields.Char(
        'Create ldap entry in subtree',
        help='Leave empty to use your LDAP base')
    create_ldap_entry_objectclass = fields.Char(
        'Object class', default='account',
        help='Separate object classes by comma if you need more than one')
    create_ldap_entry_field_mappings = fields.One2many(
        'res.company.ldap.field_mapping', 'ldap_id', string='Field mappings',
        default=_create_ldap_entry_field_mappings_default)

    @api.model
    def get_or_create_user(self, conf, login, ldap_entry):
        user_id = super(ResCompanyLdap, self).get_or_create_user(
            conf, login, ldap_entry)
        if user_id:
            self.env['res.users'].browse(user_id).write({
                'ldap_entry_dn': ldap_entry[0],
            })
        return user_id

    @api.constrains('create_ldap_entry_field_mappings')
    def _constrain_create_ldap_entry_field_mappings(self):
        for this in self:
            if len(this.create_ldap_entry_field_mappings
                   .filtered('use_for_dn')) != 1:
                raise exceptions.ValidationError(
                    _('You need to set exactly one mapping as DN'))
