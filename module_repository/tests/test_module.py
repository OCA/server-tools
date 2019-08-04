# coding: utf-8
# Copyright (C) 2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestModule(TransactionCase):

    def setUp(self):
        super(TestModule, self).setUp()
        self.ModuleModule = self.env['ir.module.module']

    # Test Section
    def test_01_module_update_list(self):

        self.ModuleModule.update_list()
        CurrentModule = self.ModuleModule.search(
            [('name', '=', 'module_repository')])[0]

        self.assertNotEqual(
            CurrentModule.repository_id, False,
            "After analyze, modules should have repository")

        repository = CurrentModule.repository_id
        self.assertEqual(
            'server-tools' in repository.url, True,
            "Bad analyze of git informations")
