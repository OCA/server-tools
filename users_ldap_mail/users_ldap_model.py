# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Daniel Reis
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

from openerp.osv import fields, orm


class CompanyLDAP(orm.Model):
    _inherit='res.company.ldap'
    _columns={
        'name_attribute': fields.char('Name Attribute', size=64,
            help="Default in 'cn'. For an AD you could use 'displayName' instead."),
        'mail_attribute': fields.char('E-mail attribute', size=64,
            help="Active Directory uses the 'mail' attribute."),
          }


    def get_ldap_dicts(self, cr, ids=None):
        """ 
        Copy of auth_ldap's funtion, changing only the SQL, so that it returns
        all fields in the table.
        """

        if ids:
            id_clause = 'AND id IN (%s)'
            args = [tuple(ids)]
        else:
            id_clause = ''
            args = []
        cr.execute("""
            SELECT *
            FROM res_company_ldap
            WHERE ldap_server != '' """ + id_clause + """ ORDER BY sequence
        """, args)
        return cr.dictfetchall()


    def map_ldap_attributes(self, cr, uid, conf, login, ldap_entry):
        values = super(CompanyLDAP, self).map_ldap_attributes(cr, uid, conf,
                    login, ldap_entry)
        if conf.get('name_attribute'):
            values['name'] = ldap_entry[1][conf['name_attribute']][0] 
        if conf.get('mail_attribute'):
            values['email'] = ldap_entry[1][conf['mail_attribute']][0] 
        return values

