# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2015 Camptocamp SA
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
import logging
import psycopg2
import openerp.exceptions
from openerp import SUPERUSER_ID
from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)


# New class to store the login date
class ResUsersLogin(orm.Model):

    _name = 'res.users.login'
    _columns = {
        'user_id': fields.many2one(
            'res.users', 'User', required=True, ondelete="cascade"),
        'login_dt': fields.date('Latest connection'),
    }

    _sql_constraints = [
        ('user_id_unique',
         'unique(user_id)',
         'The user can only have one login line!')
    ]

    # Cron method
    def cron_sync_login_date(self, cr, uid, context=None):
        # Simple SQL query to update the original login_date column.
        try:
            cr.execute("UPDATE res_users SET login_date = "
                       "(SELECT login_dt FROM res_users_login "
                       "WHERE res_users_login.user_id = res_users.id)")
            cr.commit()
        except Exception as e:
            cr.rollback()
            _logger.exception('Could not synchronize login dates: %s', e)

        return True


class ResUsers(orm.Model):

    _inherit = 'res.users'

    # Function to retrieve the login date from the res.users object
    # (used in some functions, and the user state)
    def _get_login_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        user_login_obj = self.pool['res.users.login']
        for user_id in ids:
            login_ids = user_login_obj.search(
                cr, uid, [('user_id', '=', user_id)], limit=1,
                context=context)
            if len(login_ids) == 0:
                res[user_id] = False
            else:
                login = user_login_obj.browse(cr, uid, login_ids[0],
                                              context=context)
                res[user_id] = login.login_dt
        return res

    _columns = {
        'login_date': fields.function(_get_login_date,
                                      string='Latest connection',
                                      type='date', select=1,
                                      readonly=True, store=False,
                                      nodrop=True),
    }

    # Re-defining the login function in order to use the new table
    def _login(self, db, login, password):
        if not password:
            return False
        user_id = False
        cr = self.pool.cursor()
        try:
            # check if user exists
            res = self.search(cr, SUPERUSER_ID, [('login', '=', login)])
            if res:
                user_id = res[0]
                try:
                    # check credentials
                    self.check_credentials(cr, user_id, password)
                except openerp.exceptions.AccessDenied:
                    _logger.info("Login failed for db:%s login:%s", db, login)
                    user_id = False

                if user_id:
                    try:
                        cr.execute("SELECT login_dt "
                                   "FROM res_users_login "
                                   "WHERE user_id=%s "
                                   "FOR UPDATE NOWAIT", (user_id,),
                                   log_exceptions=False)
                        # create login line if not existing
                        result = cr.fetchone()
                        if result:
                            cr.execute("UPDATE res_users_login "
                                       "SET login_dt = now() "
                                       "AT TIME ZONE 'UTC' "
                                       "WHERE user_id=%s", (user_id,))
                        else:
                            cr.execute("INSERT INTO res_users_login "
                                       "(user_id, login_dt) "
                                       "VALUES (%s, now())", (user_id,))
                        cr.commit()
                    except psycopg2.OperationalError:
                        _logger.warning("Failed to update last_login "
                                        "for db:%s login:%s",
                                        db, login, exc_info=True)
                        cr.rollback()
        except Exception as e:
            _logger.exception('Login exception: %s', e)
            user_id = False
        finally:
            cr.close()

        return user_id
