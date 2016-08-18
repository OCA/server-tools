# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestSecureUninstall(TransactionCase):

    def test_secure_uninstall_without_key(self):
        vals = {'uninstall_password': 'toto'}
        bmu = self.env['base.module.upgrade'].create(vals)
        try:
            bmu.upgrade_module()
        except Exception as e:
            messages = ('Missing configuration key',
                        'Password Error\n----------')
            self.assertIn(e.message[:25], messages)
