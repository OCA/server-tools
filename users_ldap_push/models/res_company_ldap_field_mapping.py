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
from openerp import models, fields, api


class ResCompanyLdapFieldMapping(models.Model):
    _name = 'res.company.ldap.field_mapping'
    _description = 'Mapping from Odoo fields to ldap attributes'

    field_id = fields.Many2one(
        'ir.model.fields', string='Odoo field', required=True,
        domain=lambda self: self._field_id_domain())
    attribute = fields.Char('LDAP attribute', required=True)
    use_for_dn = fields.Boolean('DN')
    ldap_id = fields.Many2one(
        'res.company.ldap', string='LDAP configuration', required=True)

    @api.model
    def _field_id_domain(self):
        return [
            ('model_id', '=', self.env.ref('base.model_res_users').id),
            ('ttype', 'in', ['selection', 'char', 'text', 'integer', 'float']),
        ]
