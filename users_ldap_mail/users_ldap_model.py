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

from openerp import models, fields
from openerp import SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


class CompanyLDAP(models.Model):
    _inherit = 'res.company.ldap'

    name_attribute = fields.Char(
        'Name Attribute',
        help=("By default 'cn' is used. or ActiveDirectory you might use "
              "'displayName' instead."),
        default='cn')
    mail_attribute = fields.Char(
        'Email Attribute',
        help="LDAP attribute to use to retrieve email address.",
        default='mail')

    def get_ldap_dicts(self, cr, ids=None):
        """
        Copy of auth_ldap's function, changing only the SQL, so that it returns
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

    def get_or_create_user(self, cr, uid, conf, login, ldap_entry,
                           context=None):
        user_id = super(CompanyLDAP, self).get_or_create_user(
            cr, uid, conf, login, ldap_entry, context)

        mapping = [
            ('name', 'name_attribute'),
            ('email', 'mail_attribute'),
        ]
        values = {}
        for value_key, conf_name in mapping:
            try:
                if conf[conf_name]:
                    values[value_key] = ldap_entry[1][conf[conf_name]][0]
            except KeyError:
                _logger.warning(
                    'No LDAP attribute "%s" found for login  "%s"'
                    % (conf.get(conf_name), values.get('login')))

        new_user = self.pool['res.users'].browse(cr, SUPERUSER_ID, user_id)
        new_user.write(values)

        return user_id
