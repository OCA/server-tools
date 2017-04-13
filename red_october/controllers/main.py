# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json

from odoo import _, http
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class RedOctoberController(http.Controller):

    @http.route([
        '/red_october/profile/password_change',
        '/red_october/profile/<int:profile_id>/password_change',
    ],
        type='http',
        auth='user',
        methods=['POST'],
    )
    def password_change(self, profile_id=None, **kwargs):
        User = http.request.env['red.october.user']
        if profile_id:
            user = User.browse(profile_id)
        else:
            user = User.get_current_user()
        return self._run_and_reply(
            user.change_password,
            kwargs['password_current'],
            kwargs['password_new'],
            kwargs['password_validate'],
        )

    @http.route([
        '/red_october/crypt/<string:command>',
        '/red_october/vault/<int:vault_id>/crypt/<string:command>',
    ],
        type='http',
        auth='user',
        methods=['POST'],
    )
    def crypt(self, command, user_id, password, data, vault_id=None,
              owner_ids=None, delegation_min=1):
        assert command in ['encrypt', 'decrypt']
        user = http.request.env['red.october.user'].browse(
            int(user_id),
        )
        command = getattr(http.request.env['red.october.file'], command)
        return self._run_and_reply(
            command,
            data=data,
            vault=vault_id,
            user=user,
            password=password,
            owner_ids=owner_ids,
            delegation_min=delegation_min,
        )

    @http.route([
        '/red_october/delegate',
        '/red_october/profile/<int:profile_id>/delegate',
        '/red_october/vault/<int:vault_id>/profile/<int:profile_id>/delegate',
    ],
        type='http',
        auth='user',
        methods=['POST'],
    )
    def delegate(self, password, profile_id=None, vault_id=None,
                 num_expire=0, date_expire=None,
                 ):

        Users = http.request.env['red.october.user']

        if profile_id is None:
            profile_id = Users.get_current_user().id

        if vault_id is None:
            vault_id = self.env.user.company_id.default_red_october_id.id

        delegation = http.request.env['red.october.delegation'].create({
            'vault_id': vault_id,
            'user_id': profile_id,
            'num_expire': num_expire,
            'date_expire': date_expire,
        })
        return self._run_and_reply(delegation.delegate, password)

    def _run_and_reply(self, callable, *args, **kwargs):
        try:
            return self._send_result(
                data=callable(*args, **kwargs),
            )
        except Exception as e:
            return self._send_result(
                errors=[e.message or e.value or e.name],
            )

    @staticmethod
    def _send_result(data=None, errors=None):
        if errors is None:
            errors = []
        return json.dumps({
            'data': data,
            'errors': errors,
        })
