# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from contextlib import contextmanager

import odoo
from odoo.tests import common
from odoo.tests.common import BaseCase, tagged

ADMIN_USER_ID = common.ADMIN_USER_ID


@contextmanager
def environment():
    """Return an environment with a new cursor for the current database; the
    cursor is committed and closed after the context block.
    """
    registry = odoo.modules.registry.Registry(common.get_db_name())
    with registry.cursor() as cr:
        yield odoo.api.Environment(cr, ADMIN_USER_ID, {})


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class Common(BaseCase):
    def setUp(self):
        super().setUp()
