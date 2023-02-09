# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.modules.registry import Registry
from odoo.tests import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # this reloads our registry, and we don't want to run tests twice
        # we also need the original registry for further tests, so save a
        # reference to it
        cls.original_registry = Registry.registries[cls.env.cr.dbname]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Force rollback to avoid unstable test database
        cls.env.cr.rollback()
        # reset afterwards
        Registry.registries[cls.env.cr.dbname] = cls.original_registry
