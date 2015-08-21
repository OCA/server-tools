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

import re
from openerp.osv import orm
import logging

_logger = logging.getLogger(__name__)

try:
    from ldap.filter import filter_format
except ImportError:
    _logger.debug('Can not `from ldap.filter import filter_format`.')


class CompanyLDAP(orm.Model):
    _inherit = 'res.company.ldap'

    def action_populate(self, cr, uid, ids, context=None):
        """
        Prepopulate the user table from one or more LDAP resources.

        Obviously, the option to create users must be toggled in
        the LDAP configuration.

        Return the number of users created (as far as we can tell).
        """
        if isinstance(ids, (int, float)):
            ids = [ids]

        users_pool = self.pool.get('res.users')
        users_no_before = users_pool.search(
            cr, uid, [], context=context, count=True)
        logger = logging.getLogger('orm.ldap')
        logger.debug("action_populate called on res.company.ldap ids %s", ids)

        for conf in self.get_ldap_dicts(cr, ids):
            if not conf['create_user']:
                continue
            attribute_match = re.search(
                r'([a-zA-Z_]+)=\%s', conf['ldap_filter'])
            if attribute_match:
                login_attr = attribute_match.group(1)
            else:
                raise orm.except_orm(
                    "No login attribute found",
                    "Could not extract login attribute from filter %s" %
                    conf['ldap_filter'])
            ldap_filter = filter_format(conf['ldap_filter'] % '*', ())
            for result in self.query(conf, ldap_filter):
                self.get_or_create_user(
                    cr, uid, conf, result[1][login_attr][0], result)

        users_no_after = users_pool.search(
            cr, uid, [], context=context, count=True)
        users_created = users_no_after - users_no_before
        logger.debug("%d users created", users_created)
        return users_created

    def populate_wizard(self, cr, uid, ids, context=None):
        """
        GUI wrapper for the populate method that reports back
        the number of users created.
        """
        if not ids:
            return
        if isinstance(ids, (int, float)):
            ids = [ids]
        wizard_obj = self.pool.get('res.company.ldap.populate_wizard')
        res_id = wizard_obj.create(
            cr, uid, {'ldap_id': ids[0]}, context=context)

        return {
            'name': wizard_obj._description,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': wizard_obj._name,
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': res_id,
            'nodestroy': True,
        }
