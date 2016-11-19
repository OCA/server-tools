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

from openerp import SUPERUSER_ID

import openerp
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers import main
from openerp.addons.auth_from_http_remote_user.model import \
    AuthFromHttpRemoteUserInstalled
from .. import utils

import random
import logging
import werkzeug

_logger = logging.getLogger(__name__)


class Home(main.Home):

    _REMOTE_USER_ATTRIBUTE = 'HTTP_REMOTE_USER'

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        main.ensure_db()
        try:
            self._bind_http_remote_user(http.request.session.db)
        except http.AuthenticationError:
            return werkzeug.exceptions.Unauthorized().get_response()
        return super(Home, self).web_client(s_action, **kw)

    def _search_user(self, res_users, login, cr):
        user_ids = res_users.search(cr, SUPERUSER_ID, [('login', '=', login),
                                                       ('active', '=', True)])
        assert len(user_ids) < 2
        if user_ids:
            return user_ids[0]
        return None

    def _bind_http_remote_user(self, db_name):
        try:
            registry = openerp.registry(db_name)
            with registry.cursor() as cr:
                if AuthFromHttpRemoteUserInstalled._name not in registry:
                    # module not installed in database,
                    # continue usual behavior
                    return

                headers = http.request.httprequest.headers.environ

                login = headers.get(self._REMOTE_USER_ATTRIBUTE, None)
                if not login:
                    # no HTTP_REMOTE_USER header,
                    # continue usual behavior
                    return

                request_login = request.session.login
                if request_login:
                    if request_login == login:
                        # already authenticated
                        return
                    else:
                        request.session.logout(keep_db=True)

                res_users = registry.get('res.users')
                user_id = self._search_user(res_users, login, cr)
                if not user_id:
                    # HTTP_REMOTE_USER login not found in database
                    request.session.logout(keep_db=True)
                    raise http.AuthenticationError()

                # generate a specific key for authentication
                key = randomString(utils.KEY_LENGTH, '0123456789abcdef')
                res_users.write(cr, SUPERUSER_ID, [user_id], {'sso_key': key})
            request.session.authenticate(db_name, login=login,
                                         password=key, uid=user_id)
        except http.AuthenticationError, e:
            raise e
        except Exception, e:
            _logger.error("Error binding Http Remote User session",
                          exc_info=True)
            raise e


randrange = random.SystemRandom().randrange


def randomString(length, chrs):
    """Produce a string of length random bytes, chosen from chrs."""
    n = len(chrs)
    return ''.join([chrs[randrange(n)] for _ in xrange(length)])
