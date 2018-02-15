# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) 2009-2016 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _login(self, db, login, password):
        """
        Call map_groups also for existing users
        in order to enforce the 'only_ldap_groups'
        security policy.
        """
        uid = super(ResUsers, self)._login(db, login, password)
        if uid:
            registry = RegistryManager.get(db)
            with registry.cursor() as cr:
                ldap_obj = registry.get('res.company.ldap')
                for ldap_config in ldap_obj.get_ldap_dicts(cr):
                    ldap_entry = ldap_obj.authenticate(
                        ldap_config, login, password)
                    if ldap_entry:
                        env = api.Environment(cr, SUPERUSER_ID, {})
                        comp_ldap = env['res.company.ldap'].browse(
                            ldap_config['id'])
                        comp_ldap.map_groups(
                            uid, ldap_config, ldap_entry)
        return uid
