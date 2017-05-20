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

        self.ProductObj = self.env['product.product']
        self.PricelistItemObj = self.env['product.pricelist.item']
        self.SuperCalendarObj = self.env['super.calendar']
        self.SuperCalendarConfiguratorObj = self.env[
            'super.calendar.configurator']
        self.SuperCalendarConfiguratorLineObj = self.env[
            'super.calendar.configurator.line']
        self.ModelFieldsObj = self.env['ir.model.fields']
        self.ModelObj = self.env['ir.model']

        self.product = self.ProductObj.browse(
            self.ref('product.product_product_consultant')
        )
        self.pricelistItem = self.PricelistItemObj.browse(
            self.ref('product.item0')
        )
        self.pricelistItem.write({
            'product_id': self.product.id
        })

        self.super_calendar_configurator = \
            self.SuperCalendarConfiguratorObj.create({
                'name': 'Pricelist item',
            })

        self.pricelistItem_model = self.ModelObj.search([
            ('model', '=', 'product.pricelist.item')
        ])
        self.date_start_field = self.ModelFieldsObj.search([
            ('name', '=', 'create_date'),
            ('model', '=', 'product.pricelist.item'),
        ])
        self.description_field = self.ModelFieldsObj.search([
            ('name', '=', 'name'),
            ('model', '=', 'product.pricelist.item'),
        ])
        self.product_field = self.ModelFieldsObj.search([
            ('name', '=', 'product_id'),
            ('model', '=', 'product.pricelist.item'),
        ])

        self.super_calendar_configurator_line = \
            self.SuperCalendarConfiguratorLineObj.create({
                'name': self.pricelistItem_model.id,
                'date_start_field_id': self.date_start_field.id,
                'description_field_id': self.description_field.id,
                'configurator_id': self.super_calendar_configurator.id,
            })

    def test_get_record_values_from_line(self):
        """
        Test if record values are correctly computed
        """

        # Test without product
        values_pricelistitem = self.super_calendar_configurator.\
            _get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )[self.pricelistItem]

        correctvalues = {
            'configurator_id': self.super_calendar_configurator.id,
            'date_start': self.pricelistItem.create_date,
            'duration': False,
            'model_id': self.pricelistItem_model.id,
            'name': self.pricelistItem.name,
            'res_id': self.pricelistItem_model.model + ',' +
            str(self.pricelistItem.id),
            'user_id': False,
            'product_id': False,
        }

        for key in ['configurator_id', 'date_start', 'duration', 'model_id',
                    'name', 'res_id', 'user_id', 'product_id']:
            self.assertEqual(
                values_pricelistitem[key],
                correctvalues[key]
            )

        # Add a product
        self.super_calendar_configurator_line.write({
            'product_field_id': self.product_field.id,
        })
        values_pricelistitem = self.super_calendar_configurator.\
            _get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )[self.pricelistItem]
        correctvalues['product_id'] = self.product.id
        self.assertEqual(
            values_pricelistitem['product_id'],
            correctvalues['product_id']
        )

        # Test Exception
        self.categ_field = self.ModelFieldsObj.search([
            ('name', '=', 'categ_id'),
            ('model', '=', 'product.pricelist.item')
        ])
        self.super_calendar_configurator_line.write({
            'product_field_id': self.categ_field.id,
        })
        with self.assertRaises(ValidationError):
            self.super_calendar_configurator._get_record_values_from_line(
                self.super_calendar_configurator.line_ids[0]
            )
