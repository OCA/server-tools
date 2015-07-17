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

from openerp import models
from openerp import fields
from openerp import api
import logging
from string import Template


class LDAPOperator(models.AbstractModel):
    _name = "res.company.ldap.operator"

    def operators(self):
        return ('contains', 'equals', 'query')

    def contains(self, ldap_entry, attribute, value, ldap_config, company,
                 logger):
        return (attribute in ldap_entry[1]) and \
            (value in ldap_entry[1][attribute])

    def equals(self, ldap_entry, attribute, value, ldap_config, company,
               logger):
        return attribute in ldap_entry[1] and \
            unicode(value) == unicode(ldap_entry[1][attribute])

    def query(self, ldap_entry, attribute, value, ldap_config, company,
              logger):
        query_string = Template(value).safe_substitute(dict(
            [(attr, ldap_entry[1][attribute][0]) for attr in ldap_entry[1]]
            )
        )
        logger.debug('evaluating query group mapping, filter: %s' %
                     query_string)
        results = company.query(ldap_config, query_string)
        logger.debug(results)
        return bool(results)


class CompanyLDAPGroupMapping(models.Model):
    _name = 'res.company.ldap.group_mapping'
    _rec_name = 'ldap_attribute'
    _order = 'ldap_attribute'

    def _get_operators(self):
        op_obj = self.env['res.company.ldap.operator']
        operators = [(op, op) for op in op_obj.operators()]
        return tuple(operators)

    ldap_id = fields.Many2one('res.company.ldap', 'LDAP server', required=True)
    ldap_attribute = fields.Char(
        'LDAP attribute',
        help='The LDAP attribute to check.\n'
             'For active directory, use memberOf.')
    operator = fields.Selection(
        _get_operators, 'Operator',
        help='The operator to check the attribute against the value\n'
        'For active directory, use \'contains\'', required=True)
    value = fields.Char(
        'Value',
        help='The value to check the attribute against.\n'
        'For active directory, use the dn of the desired group',
        required=True)
    group = fields.Many2one(
        'res.groups', 'OpenERP group',
        help='The OpenERP group to assign', required=True)


class CompanyLDAP(models.Model):
    _inherit = 'res.company.ldap'

    group_mappings = fields.One2many(
        'res.company.ldap.group_mapping',
        'ldap_id', 'Group mappings',
        help='Define how OpenERP groups are assigned to ldap users')
    only_ldap_groups = fields.Boolean(
        'Only ldap groups',
        help='If this is checked, manual changes to group membership are '
             'undone on every login (so OpenERP groups are always synchronous '
             'with LDAP groups). If not, manually added groups are preserved.')

    _default = {
        'only_ldap_groups': False,
    }

    @api.model
    def get_or_create_user(self, conf, login, ldap_entry):
        op_obj = self.env['res.company.ldap.operator']
        id_ = conf['id']
        this = self.browse(id_)
        user_id = super(CompanyLDAP, self).get_or_create_user(
            conf, login, ldap_entry)
        if not user_id:
            return user_id
        userobj = self.env['res.users']
        user = userobj.browse(user_id)
        logger = logging.getLogger('users_ldap_groups')
        if self.only_ldap_groups:
            logger.debug('deleting all groups from user %d' % user_id)
            user.write({'groups_id': [(5, )]})

        for mapping in this.group_mappings:
            operator = getattr(op_obj, mapping.operator)
            logger.debug('checking mapping %s' % mapping)
            if operator(ldap_entry, mapping['ldap_attribute'],
                        mapping['value'], conf, self, logger):
                logger.debug('adding user %d to group %s' %
                             (user_id, mapping.group.name))
                user.write({'groups_id': [(4, mapping.group.id)]})
        return user_id
