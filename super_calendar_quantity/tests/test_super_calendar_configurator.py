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


class TestSuperCalendar(TransactionCase):

    def setUp(self):
        super(TestSuperCalendar, self).setUp()

        self.PartnerObj = self.env['res.partner']
        self.SuperCalendarObj = self.env['super.calendar']
        self.SuperCalendarConfiguratorObj = self.env[
            'super.calendar.configurator']
        self.SuperCalendarConfiguratorLineObj = self.env[
            'super.calendar.configurator.line']
        self.ModelFieldsObj = self.env['ir.model.fields']
        self.ModelObj = self.env['ir.model']

        self.partner = self.PartnerObj.create({
            'name': 'Test Partner',
            'credit_limit': 400.0
        })

        self.super_calendar_configurator = \
            self.SuperCalendarConfiguratorObj.create({
                'name': 'Partners',
            })

        self.partner_model = self.ModelObj.search([
            ('model', '=', 'res.partner')
        ])
        self.date_start_field = self.ModelFieldsObj.search([
            ('name', '=', 'create_date'),
            ('model', '=', 'res.partner'),
        ])
        self.description_field = self.ModelFieldsObj.search([
            ('name', '=', 'name'),
            ('model', '=', 'res.partner'),
        ])
        # For a partner, credit_limit is a Float field so we use it to simulate
        # a quantity
        self.quantity_field = self.ModelFieldsObj.search([
            ('name', '=', 'credit_limit'),
            ('model', '=', 'res.partner'),
        ])

        self.super_calendar_configurator_line = \
            self.SuperCalendarConfiguratorLineObj.create({
                'name': self.partner_model.id,
                'date_start_field_id': self.date_start_field.id,
                'description_field_id': self.description_field.id,
                'configurator_id': self.super_calendar_configurator.id,
            })

    def test_get_record_values_from_line(self):
        """
        Test if record values are correctly computed
        """

        # Test without quantity
        values_partner = self.super_calendar_configurator.\
            _get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )[self.partner]

        correctvalues = {
            'configurator_id': self.super_calendar_configurator.id,
            'date_start': self.partner.create_date,
            'duration': False,
            'model_id': self.partner_model.id,
            'name': self.partner.name,
            'res_id': self.partner_model.model + ',' + str(self.partner.id),
            'user_id': False,
            'quantity': False,
        }

        for key in ['configurator_id', 'date_start', 'duration', 'model_id',
                    'name', 'res_id', 'user_id', 'quantity']:
            self.assertEqual(
                values_partner[key],
                correctvalues[key]
            )

        # Add a quantity
        self.super_calendar_configurator_line.write({
            'quantity_field_id': self.quantity_field.id,
        })
        values_partner = self.super_calendar_configurator.\
            _get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )[self.partner]
        correctvalues['quantity'] = self.partner.credit_limit
        self.assertEqual(
            values_partner['quantity'],
            correctvalues['quantity']
        )
