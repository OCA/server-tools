# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import TransactionCase
from openerp.exceptions import ValidationError


class TestSuperCalendar(TransactionCase):

    def setUp(self):
        super(TestSuperCalendar, self).setUp()

        self.PartnerObj = self.env['res.partner']
        self.UserObj = self.env['res.users']
        self.CountryObj = self.env['res.country']
        self.SuperCalendarObj = self.env['super.calendar']
        self.SuperCalendarConfiguratorObj = self.env[
            'super.calendar.configurator']
        self.SuperCalendarConfiguratorLineObj = self.env[
            'super.calendar.configurator.line']
        self.ModelFieldsObj = self.env['ir.model.fields']
        self.ModelObj = self.env['ir.model']

        self.partner_A = self.PartnerObj.create({
            'name': 'Partner A',
        })

        self.user_A = self.UserObj.create({
            'name': 'Partner A',
            'partner_id': self.partner_A.id,
            'company_id': 1,
            'login': 'partner_a',
        })

        self.super_calendar_configurator = \
            self.SuperCalendarConfiguratorObj.create({
                'name': 'Users',
            })

        self.user_model = self.ModelObj.search([
            ('model', '=', 'res.users')
        ])
        self.date_start_field = self.ModelFieldsObj.search([
            ('name', '=', 'create_date'),
            ('model', '=', 'res.users'),
        ])
        self.description_field = self.ModelFieldsObj.search([
            ('name', '=', 'login'),
            ('model', '=', 'res.users'),
        ])
        self.partner_field = self.ModelFieldsObj.search([
            ('name', '=', 'partner_id'),
            ('model', '=', 'res.users')
        ])

        self.super_calendar_configurator_line = \
            self.SuperCalendarConfiguratorLineObj.create({
                'name': self.user_model.id,
                'date_start_field_id': self.date_start_field.id,
                'description_field_id': self.description_field.id,
                'configurator_id': self.super_calendar_configurator.id,
                'domain': [('login', '=', self.user_A.login)]
            })

    def test_get_record_values_from_line(self):
        """
        Test if record values are correctly computed
        """

        # Test without partner
        values_user_a = {
            'configurator_id': self.super_calendar_configurator.id,
            'date_start': self.user_A.create_date,
            'duration': False,
            'model_id': self.user_model.id,
            'name': self.user_A.login,
            'res_id': self.user_model.model + ',' + str(self.user_A.id),
            'user_id': False,
            'partner_id': False,
        }
        self.assertEqual(
            self.super_calendar_configurator._get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )[self.user_A],
            values_user_a
        )

        # Add a partner
        self.super_calendar_configurator_line.write({
            'partner_field_id': self.partner_field.id,
        })
        values_user_a['partner_id'] = self.partner_A.id
        self.assertEqual(
            self.super_calendar_configurator._get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )[self.user_A],
            values_user_a
        )

        # Test Exception
        self.company_field = self.ModelFieldsObj.search([
            ('name', '=', 'company_id'),
            ('model', '=', 'res.users')
        ])
        self.super_calendar_configurator_line.write({
            'partner_field_id': self.company_field.id,
        })
        with self.assertRaises(ValidationError):
            self.super_calendar_configurator._get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )
