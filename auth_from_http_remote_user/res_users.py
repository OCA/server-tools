# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Laurent Mignon
#    Copyright 2014 'ACSONE SA/NV'
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

from openerp.modules.registry import RegistryManager
from openerp.osv import orm, fields
from openerp import SUPERUSER_ID
import openerp.exceptions
from openerp.addons.auth_from_http_remote_user import utils


class res_users(orm.Model):
    _inherit = 'res.users'

    _columns = {
        'sso_key': fields.char('SSO Key', size=utils.KEY_LENGTH,
                               readonly=True),
    }

    def copy(self, cr, uid, rid, defaults=None, context=None):
        defaults = defaults or {}
        defaults['sso_key'] = False
        return super(res_users, self).copy(cr, uid, rid, defaults, context)

    def check_credentials(self, cr, uid, password):
        try:
            return super(res_users, self).check_credentials(cr, uid, password)
        except openerp.exceptions.AccessDenied:
            res = self.search(cr, SUPERUSER_ID, [('id', '=', uid), ('sso_key', '=', password)])
            if not res:
                raise openerp.exceptions.AccessDenied()

    def check(self, db, uid, passwd):
        try:
            return super(res_users, self).check(db, uid, passwd)
        except openerp.exceptions.AccessDenied:
            if not passwd:
                raise
            with RegistryManager.get(db).cursor() as cr:
                cr.execute('''SELECT COUNT(1)
                                FROM res_users
                               WHERE id=%s
                                 AND sso_key=%s
                                 AND active=%s''', (int(uid), passwd, True))
                if not cr.fetchone()[0]:
                    raise
                self._uid_cache.setdefault(db, {})[uid] = passwd
