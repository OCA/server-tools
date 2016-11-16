# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import controllers
from . import models

import uuid


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
