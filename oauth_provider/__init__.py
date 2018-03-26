# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import controllers
from . import models

from openerp import api, SUPERUSER_ID
import uuid

import logging
_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """ Initialize oauth_identifier on res.users

    The standard initialization puts the same value for every existing record,
    which is invalid for this field.
    This is done in the pre_init_hook to be able to add the unique constrait
    on the first run, when installing the module.
    """
    _logger.info('PRE INIT HOOK')
    env = api.Environment(cr, SUPERUSER_ID, {})
    if not env['res.users']._select_column_data().get('oauth_identifier'):
        _logger.info('PRE INIT HOOK: Initalizing oauth_identifier')
        cr.execute('ALTER TABLE res_users ADD COLUMN oauth_identifier varchar')
        cr.execute('SELECT id FROM res_users')
        for user_id in cr.fetchall():
            cr.execute(
                'UPDATE res_users SET oauth_identifier = %s WHERE id = %s',
                (str(uuid.uuid4()), user_id))
