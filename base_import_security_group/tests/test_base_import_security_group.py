# coding: utf-8
# Copyright 2017 Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import tests
from openerp.tools import mute_logger


@tests.common.at_install(False)
@tests.common.post_install(True)
class TestImportGroup(tests.HttpCase):
    def setUp(self):
        super(TestImportGroup, self).setUp()
        self.group_ref = 'base_import_security_group.group_import_csv'
        self.group = self.env.ref(self.group_ref)

    def has_button_import(self, falsify=False):
        """
        Verify that the button is either visible or invisible.
        After the adjacent button is loaded, allow for a second for
        the asynchronous call to finish and update the visibility """
        code = """
        window.setTimeout(function () {
            if (%s$('.oe_list_button_import').is(':visible')) {
                console.log('ok');
            } else {
                console.log('error');
            };
        }, 1000);
        """ % ('!' if falsify else '')
        link = '/web#action=%s' % self.env.ref('base.action_res_users').id
        with mute_logger('openerp.addons.base.res.res_users'):
            # Mute debug log about failing row lock upon user login
            self.phantom_js(
                link, code, "$('button.oe_list_add').length",
                login=self.env.user.login)

    def load(self):
        self.env['res.partner'].load(
            ['name'], [['test_base_import_security_group']])
        return self.env['res.partner'].search(
            [('name', '=', 'test_base_import_security_group')])

    def test_01_in_group(self):
        """ Show import button to users in the import group """
        self.env.user.groups_id += self.group
        self.assertTrue(self.env.user.has_group(self.group_ref))
        self.has_button_import()
        self.assertTrue(self.load())

    def test_02_not_in_group(self):
        """ Don't show import button to users not in the import group """
        self.env.user.groups_id -= self.group
        self.assertFalse(self.env.user.has_group(self.group_ref))
        self.has_button_import(falsify=True)
        self.assertFalse(self.load())

    def test_03_no_group(self):
        """ When the group does not exist, allow import (monkeypatch to assume
        that this module is not installed in that case). """
        self.group.unlink()
        self.assertFalse(self.env.user.has_group(self.group_ref))
        self.assertTrue(self.load())
