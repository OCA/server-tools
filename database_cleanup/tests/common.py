# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.modules.registry import Registry
from odoo.tests import TransactionCase
from odoo.tests.common import tagged


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()
        # this reloads our registry, and we don't want to run tests twice
        # we also need the original registry for further tests, so save a
        # reference to it
        self.original_registry = Registry.registries[self.env.cr.dbname]

    def tearDown(self):
        super(Common, self).tearDown()
        # Force rollback to avoid unstable test database
        self.env.cr.rollback()
        # reset afterwards
        Registry.registries[self.env.cr.dbname] = self.original_registry
