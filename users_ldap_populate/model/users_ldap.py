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
from openerp.osv import orm, fields  # pylint: disable=W0402
from openerp import SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

try:
    import ldap
    from ldap.filter import filter_format
except ImportError:
    _logger.debug('Cannot import ldap')


class CompanyLDAP(orm.Model):
    _inherit = 'res.company.ldap'

    _columns = {
        'no_deactivate_user_ids': fields.many2many(
            'res.users', 'res_company_ldap_no_deactivate_user_rel',
            'ldap_id', 'user_id',
            'Users never to deactivate',
            help='List users who never should be deactivated by'
            ' the deactivation wizard'),
        'deactivate_unknown_users': fields.boolean(
            'Deactivate unknown users'),
    }

    _defaults = {
        'no_deactivate_user_ids': [(6, 0, [SUPERUSER_ID])],
        'deactivate_unknown_users': False,
    }

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

        deactivate_unknown = None
        known_user_ids = [uid]
        for this in self.read(cr, uid, ids,
                              [
                                  'no_deactivate_user_ids',
                                  'deactivate_unknown_users',
                              ],
                              context=context, load='_classic_write'):
            if deactivate_unknown is None:
                deactivate_unknown = True
            known_user_ids.extend(this['no_deactivate_user_ids'])
            deactivate_unknown &= this['deactivate_unknown_users']

        if deactivate_unknown:
            logger.debug("will deactivate unknown users")

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
            results = self.get_ldap_entry_dicts(conf)
            for result in results:
                user_id = self.get_or_create_user(
                    cr, uid, conf, result[1][login_attr][0], result)
                # this happens if something goes wrong while creating the user
                # or fetching information from ldap
                if not user_id:
                    deactivate_unknown = False
                known_user_ids.append(user_id)

        users_no_after = users_pool.search(
            cr, uid, [], context=context, count=True)
        users_created = users_no_after - users_no_before

        deactivated_users_count = 0
        if deactivate_unknown:
            deactivated_users_count = self.do_deactivate_unknown_users(
                cr, uid, ids, known_user_ids, context=context)

        logger.debug("%d users created", users_created)
        logger.debug("%d users deactivated", deactivated_users_count)
        return users_created, deactivated_users_count

    def do_deactivate_unknown_users(
            self, cr, uid, ids, known_user_ids, context=None):
        """
        Deactivate users not found in last populate run
        """
        res_users = self.pool.get('res.users')
        unknown_user_ids = []
        for unknown_user in res_users.read(
                cr, uid,
                res_users.search(
                    cr, uid,
                    [('id', 'not in', known_user_ids)],
                    context=context),
                ['login'],
                context=context):
            present_in_ldap = False
            for conf in self.get_ldap_dicts(cr, ids):
                present_in_ldap |= bool(self.get_ldap_entry_dicts(
                    conf, user_name=unknown_user['login']))
            if not present_in_ldap:
                res_users.write(
                    cr, uid, unknown_user['id'], {'active': False},
                    context=context)
                unknown_user_ids.append(unknown_user['id'])

        return len(unknown_user_ids)

    def get_ldap_entry_dicts(self, conf, user_name='*'):
        """
        Execute ldap query as defined in conf

        Don't call self.query because it supresses possible exceptions
        """
        ldap_filter = filter_format(conf['ldap_filter'] % user_name, ())
        conn = self.connect(conf)
        conn.simple_bind_s(conf['ldap_binddn'] or '',
                           conf['ldap_password'] or '')
        results = conn.search_st(conf['ldap_base'], ldap.SCOPE_SUBTREE,
                                 ldap_filter.encode('utf8'), None,
                                 timeout=60)
        conn.unbind()

        return results

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
