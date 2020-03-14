# Copyright 2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCompanyCountry(TransactionCase):

    def setUp(self):
        super(TestCompanyCountry, self).setUp()
        self.wizard = self.env['company.country.config.settings']
        self.us_country = self.env.ref('base.us')
        self.mx_country = self.env.ref('base.mx')
        self.main_company = self.env.ref('base.main_company')
        self.module_account = self.env.ref('base.module_account')
        self.main_company.write({'country_id': self.us_country.id})
        self.module_account.write({'state': 'uninstalled'})
        self.env_country = os.environ.get('COUNTRY')

    def tearDown(self):
        super(TestCompanyCountry, self).tearDown()
        os.environ['COUNTRY'] = self.env_country

    def test01_company_country_changed(self):
        self.wizard.load_company_country(country_code='MX')
        self.assertEqual(self.main_company.country_id, self.mx_country)

    def test02_country_environment_values(self):
        # Country Code unknown, should raise
        with self.assertRaises(ValidationError):
            self.wizard.load_company_country(country_code='BAD')

        # COUNTRY as empty string, should unset Country of main company
        os.environ['COUNTRY'] = ""
        self.wizard.load_company_country()
        self.assertEqual(self.main_company.country_id.id, False)

        # COUNTRY environment variable not set, should raise
        with self.assertRaises(ValidationError):
            l10n_to_install = self.env['ir.module.module'].search([
                ('state', '=', 'to install'),
                ('name', '=like', 'l10n_%')])
            l10n_to_install.write({'state': 'uninstalled'})
            del os.environ['COUNTRY']
            self.wizard.load_company_country()

        # Account is already installed, shouldn't raise
        self.module_account.write({'state': 'installed'})
        self.wizard.load_company_country()
