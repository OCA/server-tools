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
from .. import utils

import random
import logging
import werkzeug

_logger = logging.getLogger(__name__)


class Home(main.Home):

    _REQUIRED_ATTRIBUTES = ['HTTP_REMOTE_USER']
    _OPTIONAL_ATTRIBUTES = []

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        main.ensure_db()
        if not request.session.uid:
            try:
                self._bind_http_remote_user(http.request.session.db)
            except http.AuthenticationError:
                return werkzeug.exceptions.Unauthorized()
        return super(Home, self).web_client(s_action, **kw)

    def _get_user_id_from_attributes(self, res_users, cr, attrs):
        login = attrs.get('HTTP_REMOTE_USER', None)
        user_ids = res_users.search(cr, SUPERUSER_ID, [('login', '=', login),
                                                       ('active', '=', True)])
        assert len(user_ids) < 2
        if user_ids:
            return user_ids[0]
        return None

    def _get_attributes_form_header(self):
        attrs = {}

        all_attrs = self._REQUIRED_ATTRIBUTES + self._OPTIONAL_ATTRIBUTES

        headers = http.request.httprequest.headers.environ

        for attr in all_attrs:
            value = headers.get(attr, None)
            if value is not None:
                attrs[attr] = value

        attrs_found = set(attrs.keys())
        attrs_missing = set(all_attrs) - attrs_found
        if len(attrs_found) > 0:
            _logger.debug("Fields '%s' not found in http headers\n %s",
                          attrs_missing, headers)

        missings = set(self._REQUIRED_ATTRIBUTES) - attrs_found
        if len(missings) > 0:
            _logger.error("Required fields '%s' not found in http headers\n %s",
                          missings, headers)
        return attrs

    def _bind_http_remote_user(self, db_name):
        try:
            registry = openerp.registry(db_name)
            with registry.cursor() as cr:
                modules = registry.get('ir.module.module')
                domain = ['&',
                          ('name', '=', 'auth_from_http_remote_user'),
                          ('state', '=', 'installed')]
                installed = modules.search_count(cr, SUPERUSER_ID, domain) == 1
                if not installed:
                    return
                config = registry.get('auth_from_http_remote_user.'
                                      'config.settings')
                # get parameters for SSO
                default_login_page_disabled = \
                    config.is_default_login_page_disabled(cr,
                                                          SUPERUSER_ID,
                                                          None)

                # get the user
                res_users = registry.get('res.users')
                attrs = self._get_attributes_form_header()
                user_id = self._get_user_id_from_attributes(res_users,
                                                            cr,
                                                            attrs)

                if user_id is None:
                    if default_login_page_disabled:
                        raise http.AuthenticationError()
                    return

                # generate a specific key for authentication
                key = randomString(utils.KEY_LENGTH, '0123456789abcdef')
                res_users.write(cr, SUPERUSER_ID, [user_id], {'sso_key': key})
                login = res_users.browse(cr, SUPERUSER_ID, user_id).login
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
