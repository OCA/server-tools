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
        # Registry.new is forbidden while testing: keep the in-memory registry
        # sequence aligned with the database one so that opening a new
        # transaction does not try to rebuild the registry after the purge
        # wizards signaled their changes.
        registry.registry_sequence = registry.get_sequences(cr)[0]
        env = odoo.api.Environment(cr, ADMIN_USER_ID, {})
        env.user.group_ids |= env.ref("base.group_system")
        yield env
        # The tests adjust the in-memory registry themselves: do not let the
        # commit signal a registry change, the transaction would otherwise
        # try to rebuild the registry with Registry.new (forbidden in tests).
        env.cr.flush()
        env.transaction._registry_invalidated = 0


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class Common(BaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
