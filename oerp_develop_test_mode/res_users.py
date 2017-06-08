# -*- coding: utf-8 -*-
##############################################################################
#
#    BizzAppDev
#    Copyright (C) 2004-TODAY bizzappdev(<http://www.bizzappdev.com>).
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

from openerp.osv import osv
from openerp.tools import config
from openerp import SUPERUSER_ID
from openerp import pooler

DEVELOP = False
TEST = False


class res_users(osv.osv):
    _inherit = 'res.users'

    def __set_from_config_test(self, db):
        cr = pooler.get_db(db).cursor()
        config_parameters = self.pool.get("ir.config_parameter")
        if DEVELOP:
            config_parameters.set_param(
                cr, SUPERUSER_ID, "develop", DEVELOP)
        if TEST:
            config_parameters.set_param(
                cr, SUPERUSER_ID, "test", TEST)

        if not config.get('test'):
            config['test'] = {}

        if not config.get('develop'):
            config['develop'] = {}

        if db not in config['test']:
            ir_config_val = self.pool.get("ir.config_parameter").get_param(
                cr, SUPERUSER_ID, "test", default=None)
            config['test'][db] = ir_config_val

        if db not in config['develop']:
            ir_config_val = self.pool.get("ir.config_parameter").get_param(
                cr, SUPERUSER_ID, "develop", default=None)
            config['develop'][db] = ir_config_val
        cr.close()

    def check(self, db, uid, passwd):
        self.__set_from_config_test(db)
        return super(res_users, self).check(db, uid, passwd)

    def authenticate(self, db, login, password, user_agent_env):
        self.__set_from_config_test(db)
        return super(res_users, self).authenticate(db, login, password,
                                                   user_agent_env)

res_users()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
