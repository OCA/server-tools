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
from string import Template


class LDAPOperator:
    pass


class contains(LDAPOperator):
    def check_value(self, ldap_entry, attribute, value, ldap_config, company, logger):
        return (attribute in ldap_entry[1]) and (value in ldap_entry[1][attribute])


class equals(LDAPOperator):
    def check_value(self, ldap_entry, attribute, value, ldap_config, company, logger):
        return attribute in ldap_entry[1] and unicode(value) == unicode(ldap_entry[1][attribute])


class query(LDAPOperator):
    def check_value(self, ldap_entry, attribute, value, ldap_config, company, logger):
        query_string = Template(value).safe_substitute(dict(
            [(attr, ldap_entry[1][attribute][0]) for attr in ldap_entry[1]]
            )
        )
        logger.debug('evaluating query group mapping, filter: %s' % query_string)
        results = company.query(ldap_config, query_string)
        logger.debug(results)
        return bool(results)
