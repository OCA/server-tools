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
from openerp import _, models, fields, api, exceptions
import logging

_logger = logging.getLogger(__name__)

try:
    import ldap
    import ldap.modlist
except ImportError:
    _logger.debug('Can not `from ldap.filter import filter_format`.')


class ResUsers(models.Model):
    _inherit = 'res.users'

    ldap_entry_dn = fields.Char('LDAP DN', readonly=True)
    is_ldap_user = fields.Boolean(
        'LDAP user', compute='_compute_is_ldap_user', default=True)

    @api.model
    @api.returns('self', lambda record: record.id)
    def create(self, values):
        result = super(ResUsers, self).create(values)
        result.push_to_ldap(values)
        return result

    @api.multi
    def write(self, values):
        result = super(ResUsers, self).write(values)
        self.push_to_ldap(values)
        return result

    @api.multi
    def _push_to_ldap_possible(self, values):
        return bool(self._get_ldap_configuration())

    @api.multi
    def _get_ldap_configuration(self):
        self.ensure_one()
        return self.sudo().company_id.ldaps.filtered('create_ldap_entry')[:1]

    @api.multi
    def _get_ldap_values(self, values):
        self.ensure_one()
        conf = self._get_ldap_configuration()
        result = {}
        for mapping in conf.create_ldap_entry_field_mappings:
            field_name = mapping.field_id.name
            if field_name not in values or not values[field_name]:
                continue
            result[str(mapping.attribute)] = [str(values[field_name])]
        if result:
            result['objectClass'] = conf.create_ldap_entry_objectclass\
                .encode('utf-8').split(',')
        return result

    @api.multi
    def _get_ldap_dn(self, values):
        self.ensure_one()
        conf = self._get_ldap_configuration()
        dn = conf.create_ldap_entry_field_mappings.filtered('use_for_dn')
        assert dn, 'No DN attribute mapping given!'
        assert self[dn.field_id.name], 'DN attribute empty!'
        return '%s=%s,%s' % (
            dn.attribute,
            ldap.dn.escape_dn_chars(self[dn.field_id.name].encode('utf-8')),
            conf.create_ldap_entry_base or conf.ldap_base)

    @api.multi
    def push_to_ldap(self, values):
        for this in self:
            if not values.get('is_ldap_user') and not this.is_ldap_user:
                continue
            if not this._push_to_ldap_possible(values):
                continue
            ldap_values = this._get_ldap_values(values)
            if not ldap_values:
                continue
            ldap_configuration = this._get_ldap_configuration()
            ldap_connection = ldap_configuration.connect(
                ldap_configuration.read()[0])
            ldap_connection.simple_bind_s(
                (ldap_configuration.ldap_binddn or '').encode('utf-8'),
                (ldap_configuration.ldap_password or '').encode('utf-8'))

            try:
                if not this.ldap_entry_dn:
                    this._push_to_ldap_create(
                        ldap_connection, ldap_configuration, values,
                        ldap_values)
                if this.ldap_entry_dn:
                    this._push_to_ldap_write(
                        ldap_connection, ldap_configuration, values,
                        ldap_values)
            except ldap.LDAPError as e:
                _logger.exception(e)
                raise exceptions.Warning(_('Error'), e.message)
            finally:
                ldap_connection.unbind_s()

    @api.multi
    def _push_to_ldap_create(self, ldap_connection, ldap_configuration, values,
                             ldap_values):
        self.ensure_one()
        dn = self._get_ldap_dn(values)
        ldap_connection.add_s(
            dn,
            ldap.modlist.addModlist(ldap_values))
        self.write({'ldap_entry_dn': dn})

    @api.multi
    def _push_to_ldap_write(self, ldap_connection, ldap_configuration, values,
                            ldap_values):
        self.ensure_one()
        dn = self.ldap_entry_dn.encode('utf-8')
        dn_mapping = ldap_configuration.create_ldap_entry_field_mappings\
            .filtered('use_for_dn')
        if dn_mapping.attribute in ldap_values:
            ldap_values.pop(dn_mapping.attribute)
        ldap_entry = ldap_connection.search_s(
            dn, ldap.SCOPE_BASE, '(objectClass=*)',
            map(lambda x: x.encode('utf-8'), ldap_values.keys()))
        assert ldap_entry, '%s not found!' % self.ldap_entry_dn
        ldap_entry = ldap_entry[0][1]
        ldap_connection.modify_s(
            dn,
            ldap.modlist.modifyModlist(ldap_entry, ldap_values))

    @api.one
    @api.depends('ldap_entry_dn')
    def _compute_is_ldap_user(self):
        self.is_ldap_user = bool(self.ldap_entry_dn)

    @api.one
    def _change_ldap_password(self, new_passwd, auth_dn=None,
                              auth_passwd=None):
        ldap_configuration = self.env.user.sudo()._get_ldap_configuration()
        ldap_connection = ldap_configuration.connect(
            ldap_configuration.read()[0])
        dn = auth_dn or ldap_configuration.ldap_binddn
        old_passwd = auth_passwd or ldap_configuration.ldap_password
        ldap_connection.simple_bind_s(
            dn.encode('utf-8'), old_passwd.encode('utf-8'))
        self.env['ir.model.access'].check('res.users', 'write')
        self.env.user.check_access_rule('write')
        try:
            ldap_connection.passwd_s(
                self.ldap_entry_dn, None, new_passwd.encode('utf-8'))
        except ldap.LDAPError, e:
            raise exceptions.Warning(_('Error'), e.message)
        finally:
            ldap_connection.unbind_s()
        return True

    @api.model
    def change_password(self, old_passwd, new_passwd):
        if self.env.user.is_ldap_user:
            return self.env.user._change_ldap_password(
                new_passwd, auth_dn=self.env.user.ldap_entry_dn,
                auth_passwd=old_passwd)
        return super(ResUsers, self).change_password(old_passwd, new_passwd)
