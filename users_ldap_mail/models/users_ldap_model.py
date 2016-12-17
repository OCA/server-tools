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

from odoo import models, fields

import logging
_log = logging.getLogger(__name__)


class CompanyLDAP(models.Model):
    _inherit = 'res.company.ldap'

    name_attribute = fields.Char(
        'Name Attribute', size=64, _defaults='cn',
        help="By default 'cn' is used. "
             "For ActiveDirectory you might use 'displayName' instead.")
    mail_attribute = fields.Char(
        'E-mail attribute', size=64, _defaults='mail',
        help="LDAP attribute to use to retrieve em-mail address.")

    def get_ldap_dicts(self):
        """
        Copy of auth_ldap's funtion, changing only the SQL, so that it returns
        all fields in the table.
        """
        ldaps = self.sudo().search([('ldap_server', '!=', False)],
                                   order='sequence')
        res = ldaps.read([])
        return res

    def map_ldap_attributes(self, conf, login, ldap_entry):
        values = super(CompanyLDAP, self).map_ldap_attributes(conf, login,
                                                              ldap_entry)
        mapping = [
            ('name', 'name_attribute'),
            ('email', 'mail_attribute'),
        ]
        for value_key, conf_name in mapping:
            try:
                if conf[conf_name]:
                    values[value_key] = ldap_entry[1][conf[conf_name]][0]
            except KeyError:
                _log.warning('No LDAP attribute "%s" found for login  "%s"' % (
                    conf.get(conf_name), values.get('login')))
        return values
