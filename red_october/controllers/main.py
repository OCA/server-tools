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
    def password_change_post(self, profile_id=None, **kwargs):
        User = http.request.env['red.october.user']
        result = None
        errors = []
        if not profile_id:
            user = User.get_current_user()
        else:
            user = User.browse(profile_id)
        try:
            result = user.change_password(
                kwargs['password_current'],
                kwargs['password_new'],
                kwargs['password_validate'],
            )
        except Exception as e:
            errors = [e.message or e.value or e.name]
        _logger.debug('Password Change Post.\n%s\n%s', kwargs, result)
        return RedOctoberController._send_result(result, errors)

    @staticmethod
    def _send_result(data=None, errors=None):
        if errors is None:
            errors = []
        return json.dumps({
            'data': data,
            'errors': errors,
        })
