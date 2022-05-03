# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from contextlib import contextmanager

import odoo
from odoo.tests import common
from odoo.tests.common import TransactionCase, tagged


@contextmanager
def new_rollbacked_env():
    registry = odoo.registry(common.get_db_name())
    uid = odoo.SUPERUSER_ID
    cr = registry.cursor()
    try:
        yield odoo.api.Environment(cr, uid, {})
    finally:
        cr.rollback()  # we shouldn't have to commit anything
        cr.close()


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()
