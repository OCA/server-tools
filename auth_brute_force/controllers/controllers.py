# -*- encoding: utf-8 -*-
##############################################################################
#
#    Authentification - Track And Prevent Brute-force Attack module for Odoo
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

import logging

from openerp import fields, http, registry, SUPERUSER_ID
from openerp.http import request
from openerp.addons.web.controllers.main import Home, ensure_db

_logger = logging.getLogger(__name__)


class LoginController(Home):
    @http.route()
    def web_login(self, redirect=None, **kw):

        if request.httprequest.method == 'POST':
            ensure_db()
            remote = request.httprequest.remote_addr
            # Get registry and cursor
            config_obj = registry(request.session.db)['ir.config_parameter']
            attempt_obj = registry(
                request.session.db)['res.authentication.attempt']
            banned_remote_obj = registry(
                request.session.db)['res.banned.remote']
            cursor = attempt_obj.pool.cursor()

            # Get Settings
            config_id = config_obj.search(cursor, SUPERUSER_ID, [(
                'key', '=',
                'auth_brute_force.max_attempt_qty')])
            max_attempts_qty = int(config_obj.browse(
                cursor, SUPERUSER_ID, config_id).value)

            # Test if remote user is banned
            banned = banned_remote_obj.search(cursor, SUPERUSER_ID, [
                ('remote', '=', remote)])
            if banned:
                _logger.warning(
                    "Authentication tried from remote '%s'. The request has"
                    " been ignored because the remote has been banned after"
                    " %d attempts without success. Login tried : '%s'." % (
                        remote, max_attempts_qty, request.params['login']))
                request.params['password'] = ''

            else:
                # Try to authenticate
                result = request.session.authenticate(
                    request.session.db, request.params['login'],
                    request.params['password'])

            # Log attempt
            attempt_obj.create(cursor, SUPERUSER_ID, {
                'attempt_date': fields.Datetime.now(),
                'login': request.params['login'],
                'remote': remote,
                'result': banned and 'banned' or (
                    result and 'successfull' or 'failed'),
            })
            cursor.commit()
            if not banned and not result:
                # Get last bad attempts quantity
                attempts_qty = len(attempt_obj.search_last_failed(
                    cursor, SUPERUSER_ID, remote))

                if max_attempts_qty <= attempts_qty:
                    # We ban the remote
                    _logger.warning(
                        "Authentication failed from remote '%s'. "
                        "The remote has been banned. Login tried : '%s'." % (
                            remote, request.params['login']))
                    banned_remote_obj.create(cursor, SUPERUSER_ID, {
                        'remote': remote,
                        'ban_date': fields.Datetime.now(),
                    })
                    cursor.commit()

                else:
                    _logger.warning(
                        "Authentication failed from remote '%s'."
                        " Login tried : '%s'. Attempt %d / %d." % (
                            remote, request.params['login'], attempts_qty,
                            max_attempts_qty))
            cursor.close()

        return super(LoginController, self).web_login(redirect=redirect, **kw)
