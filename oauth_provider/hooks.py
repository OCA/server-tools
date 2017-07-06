# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import uuid

from odoo import http

from .http import _handle_exception, __init__


def pre_init_hook(cr):
    """ Initialize oauth_identifier on res.users

    The standard initialization puts the same value for every existing record,
    which is invalid for this field.
    This is done in the pre_init_hook to be able to add the unique constrait
    on the first run, when installing the module.
    """
    cr.execute('ALTER TABLE res_users ADD COLUMN oauth_identifier varchar')
    cr.execute('SELECT id FROM res_users')
    for user_id in cr.fetchall():
        cr.execute(
            'UPDATE res_users SET oauth_identifier = %s WHERE id = %s',
            (str(uuid.uuid4()), user_id))


def post_load():
    """Monkey patch HTTP methods."""
    # http.JsonRequest._json_response = _json_response
    http.JsonRequest._handle_exception = _handle_exception
    http.JsonRequest.__init__ = __init__
