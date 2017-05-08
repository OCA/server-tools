# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _
from odoo.exceptions import ValidationError


def pre_init_hook_login_check(cr):
    """This hook will look to see if any conflicting logins exist before
    the module is installed
    :param openerp.sql_db.Cursor cr:
        Database cursor.
    """
    with cr.savepoint():
        users = []
        cr.execute("SELECT login FROM res_users")
        for user in cr.fetchall():
            login = user[0].lower()
            if login not in users:
                users.append(login)
            else:
                raise ValidationError(
                    _('Conflicting user logins exist for `%s`' % login)
                )


def post_init_hook_login_convert(cr, registry):
    """After the module is installed, set all logins to lowercase
    :param openerp.sql_db.Cursor cr:
        Database cursor.
    :param openerp.modules.registry.RegistryManager registry:
        Database registry, using v7 api.
    """
    with cr.savepoint():
        cr.execute("UPDATE res_users SET login=lower(login)")
