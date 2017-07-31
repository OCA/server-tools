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
from openerp.osv import orm, fields  # pylint: disable=W0402


class CompanyLDAPPopulateWizard(orm.TransientModel):
    _name = 'res.company.ldap.populate_wizard'
    _description = 'Populate users from LDAP'
    _columns = {
        'name': fields.char('Name', size=16),
        'ldap_id': fields.many2one(
            'res.company.ldap', 'LDAP Configuration'),
        'users_created': fields.integer(
            'Number of users created', readonly=True),
        'users_deactivated': fields.integer(
            'Number of users deactivated', readonly=True),
    }

    def create(self, cr, uid, vals, context=None):
        ldap_pool = self.pool.get('res.company.ldap')
        if 'ldap_id' in vals:
            vals['users_created'], vals['users_deactivated'] =\
                ldap_pool.action_populate(
                    cr, uid, vals['ldap_id'], context=context)
        return super(CompanyLDAPPopulateWizard, self).create(
            cr, uid, vals, context=None)
