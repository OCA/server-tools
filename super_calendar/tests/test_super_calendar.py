# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2012      Agile Business Group sagl (<http://www.agilebg.com>)
#        (c) 2012      Domsense srl (<http://www.domsense.com>)
#        (c) 2015      Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                      Alejandro Santana <alejandrosantana@anubia.es>
#        (c) 2015      Savoir-faire Linux <http://www.savoirfairelinux.com>)
#                      Agathe Mollé <agathe.molle@savoirfairelinux.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#
##############################################################################

from openerp.tests import TransactionCase
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, \
    DEFAULT_SERVER_DATE_FORMAT


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

        self.partner_A = self.PartnerObj.create({
            'name': 'Partner A',
            'date': (datetime.today() + relativedelta(days=3)),
            'email': 'Partner A email'
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

        self.super_calendar_configurator_line = \
            self.SuperCalendarConfiguratorLineObj.create({
                'name': self.partner_model.id,
                'date_start_field_id': self.date_start_field.id,
                'description_field_id': self.description_field.id,
                'configurator_id': self.super_calendar_configurator.id,
                'domain': [('name', '=', self.partner_A.name)]
            })

    def test_get_record_values_from_line(self):
        """
        Test if record values are correctly computed
        """

        # Test without any date_stop or duration
        values_partner_a = {
            'configurator_id': self.super_calendar_configurator.id,
            'date_start': self.partner_A.create_date,
            'duration': False,
            'model_id': self.partner_model.id,
            'name': self.partner_A.name,
            'res_id': self.partner_model.model+','+str(self.partner_A.id),
            'user_id': False
        }
        self.assertEqual(
            self.super_calendar_configurator._get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )[self.partner_A],
            values_partner_a
        )

        # Add a date_stop
        self.date_stop_field = self.ModelFieldsObj.search([
            ('name', '=', 'date'),
            ('model', '=', 'res.partner'),
        ])
        start_date = datetime.strptime(self.partner_A.create_date,
                                       DEFAULT_SERVER_DATETIME_FORMAT)
        stop_date = datetime.strptime(self.partner_A.date,
                                      DEFAULT_SERVER_DATE_FORMAT)
        date_diff = (stop_date - start_date)
        self.super_calendar_configurator_line.write({
            'date_stop_field_id': self.date_stop_field.id,
        })
        values_partner_a['duration'] = date_diff.total_seconds() / 3600
        self.assertEqual(
            self.super_calendar_configurator._get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )[self.partner_A],
            values_partner_a
        )

        # Test description code
        self.super_calendar_configurator2 = \
            self.SuperCalendarConfiguratorObj.create({
                'name': 'Partners 2',
            })
        self.super_calendar_configurator_line2 = \
            self.SuperCalendarConfiguratorLineObj.create({
                'name': self.partner_model.id,
                'date_start_field_id': self.date_start_field.id,
                'description_type': 'code',
                'description_code': '${o.email}',
                'configurator_id': self.super_calendar_configurator2.id,
                'domain': [('name', '=', self.partner_A.name)]
            })
        values_partner_a['name'] = self.partner_A.email
        values_partner_a['duration'] = False
        values_partner_a['configurator_id'] = \
            self.super_calendar_configurator2.id
        self.assertEqual(
            self.super_calendar_configurator2._get_record_values_from_line(
                self.super_calendar_configurator2.line_ids[0]
            )[self.partner_A],
            values_partner_a
        )

    def test_generate_calendar_records(self):
        """
        Test if calendar records are effectively created
        """
        self.super_calendar_configurator.generate_calendar_records()
        super_calendar_record = self.SuperCalendarObj.search([
            ('name', '=', self.partner_A.name)
        ])
        self.assertEqual(
            super_calendar_record.date_start,
            self.partner_A.create_date
        )
