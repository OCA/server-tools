# -*- coding: utf-8 -*-
# Copyright 2015 GRAP - Sylvain LE GAL
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, http, registry, SUPERUSER_ID
from odoo.api import Environment
from odoo.http import request
from odoo.addons.web.controllers.main import Home, ensure_db

_logger = logging.getLogger(__name__)


class LoginController(Home):

    @http.route()
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == 'POST':
            ensure_db()
            remote = request.httprequest.remote_addr
            # Get registry and cursor
            with registry(request.session.db).cursor() as cursor:
                env = Environment(cursor, SUPERUSER_ID, {})
                config_obj = env['ir.config_parameter']
                attempt_obj = env['res.authentication.attempt']
                banned_remote_obj = env['res.banned.remote']
                # Get Settings
                max_attempts_qty = int(config_obj.get_param(
                    'auth_brute_force.max_attempt_qty'))

                password = request.params['password']
                # Test if remote user is banned
                banned = banned_remote_obj.search([('remote', '=', remote)])
                if banned:
                    request.params['password'] = ''
                    _logger.warning(
                        "Authentication tried from remote '%s'. The request "
                        "has been ignored because the remote has been banned "
                        "after %d attempts without success. Login tried : '%s'"
                        "." % (remote, max_attempts_qty,
                               request.params['login']))
                else:
                    # Try to authenticate
                    result = request.session.authenticate(
                        request.session.db, request.params['login'],
                        request.params['password'])
                # Log attempt
                attempt = attempt_obj.create({
                    'attempt_date': fields.Datetime.now(),
                    'login': request.params['login'],
                    'remote': remote,
                    'result': banned and 'banned' or (
                        result and 'successfull' or 'failed'),
                    })
                cursor.commit()
                if not banned and not result:
                    # Get last bad attempts quantity
                    attempts_qty = len(attempt_obj.search_last_failed(remote))
                    if max_attempts_qty <= attempts_qty:
                        # We ban the remote
                        _logger.warning(
                            "Authentication failed from remote '%s'. "
                            "The remote has been banned. Login tried : '%s'"
                            "." % (remote, request.params['login']))
                        banned_remote_obj.sudo().create({
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

                if int(config_obj.get_param(
                    'auth_brute_force.save_passwords')):
                    if attempt and (banned or not result):
                        attempt.write({'password': password})

        return super(LoginController, self).web_login(redirect=redirect, **kw)
