# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
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

from odoo import models, fields, api


class CompanyLDAPPopulateWizard(models.TransientModel):
    _name = 'res.company.ldap.populate_wizard'
    _description = 'Populate users from LDAP'

    name = fields.Char('Name', size=16)
    ldap_id = fields.Many2one(
        'res.company.ldap',
        'LDAP Configuration'
    )
    users_created = fields.Integer(
        'Number of users created',
        readonly=True
    )

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if 'ldap_id' in vals:
            ldap = self.env['res.company.ldap'].browse(vals['ldap_id'])
            vals['users_created'] = ldap.action_populate()
        return super(CompanyLDAPPopulateWizard, self).create(vals)
