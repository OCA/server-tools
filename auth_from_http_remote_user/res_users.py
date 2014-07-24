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

from openerp import tools
from openerp.modules.registry import RegistryManager
from openerp.osv import orm, fields
import openerp.exceptions
from openerp.addons.auth_from_http_remote_user import utils


class res_users(orm.Model):
    _inherit = 'res.users'

    _columns = {
        'sso_key': fields.char('SSO Key', size=utils.KEY_LENGTH,
                               readonly=True),
    }

    def copy(self, cr, uid, rid, defaults=None, context=None):
        defaults['sso_key'] = False
        return super(res_users, self).copy(cr, uid, rid, defaults, context)

    def login(self, db, login, password):
        result = super(res_users, self).login(db, login, password)
        if result:
            return result
        else:
            with RegistryManager.get(db).cursor() as cr:
                cr.execute("""UPDATE res_users
                                SET login_date=now() AT TIME ZONE 'UTC'
                                WHERE login=%s AND sso_key=%s AND active=%s RETURNING id""",
                           (tools.ustr(login), tools.ustr(password), True))
                res = cr.fetchone()
                cr.commit()
                return res[0] if res else False

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
