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

        self.AnalyticObj = self.env['account.analytic.account']
        self.SuperCalendarObj = self.env['super.calendar']
        self.SuperCalendarConfiguratorObj = self.env[
            'super.calendar.configurator']
        self.SuperCalendarConfiguratorLineObj = self.env[
            'super.calendar.configurator.line']
        self.ModelFieldsObj = self.env['ir.model.fields']
        self.ModelObj = self.env['ir.model']

        self.parent = self.AnalyticObj.create({
            'name': 'Parent',
        })
        self.analytic = self.AnalyticObj.create({
            'name': 'Test analytic',
            'parent_id': self.parent.id
        })

        self.super_calendar_configurator = \
            self.SuperCalendarConfiguratorObj.create({
                'name': 'Analytic',
            })

        self.analytic_model = self.ModelObj.search([
            ('model', '=', 'account.analytic.account')
        ])
        self.date_start_field = self.ModelFieldsObj.search([
            ('name', '=', 'create_date'),
            ('model', '=', 'account.analytic.account'),
        ])
        self.description_field = self.ModelFieldsObj.search([
            ('name', '=', 'name'),
            ('model', '=', 'account.analytic.account'),
        ])
        self.analytic_field = self.ModelFieldsObj.search([
            ('name', '=', 'parent_id'),
            ('model', '=', 'account.analytic.account'),
        ])

        self.super_calendar_configurator_line = \
            self.SuperCalendarConfiguratorLineObj.create({
                'name': self.analytic_model.id,
                'date_start_field_id': self.date_start_field.id,
                'description_field_id': self.description_field.id,
                'configurator_id': self.super_calendar_configurator.id,
            })

    def test_get_record_values_from_line(self):
        """
        Test if record values are correctly computed
        """

        # Test without analytic account
        values_analytic = self.super_calendar_configurator.\
            _get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )[self.analytic]

        correctvalues = {
            'configurator_id': self.super_calendar_configurator.id,
            'date_start': self.analytic.create_date,
            'duration': False,
            'model_id': self.analytic_model.id,
            'name': self.analytic.name,
            'res_id': self.analytic_model.model + ',' + str(self.analytic.id),
            'user_id': False,
            'analytic_id': False,
        }

        for key in ['configurator_id', 'date_start', 'duration', 'model_id',
                    'name', 'res_id', 'user_id', 'analytic_id']:
            self.assertEqual(
                values_analytic[key],
                correctvalues[key]
            )

        # Add an analytic account
        self.super_calendar_configurator_line.write({
            'analytic_field_id': self.analytic_field.id,
        })
        values_analytic = self.super_calendar_configurator.\
            _get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )[self.analytic]
        correctvalues['analytic_id'] = self.parent.id
        self.assertEqual(
            values_analytic['analytic_id'],
            correctvalues['analytic_id']
        )

        # Test Exception
        self.partner_field = self.ModelFieldsObj.search([
            ('name', '=', 'partner_id'),
            ('model', '=', 'account.analytic.account')
        ])
        self.super_calendar_configurator_line.write({
            'analytic_field_id': self.partner_field.id,
        })
        with self.assertRaises(ValidationError):
            self.super_calendar_configurator._get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )
