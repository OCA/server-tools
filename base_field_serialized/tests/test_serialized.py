# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
from openerp import models, fields
from openerp.tests.common import TransactionCase


class BaseFieldSerializedTestModel(models.Model):
    _name = 'base.field.serialized.test.model'

    serialized = fields.Serialized('Serialized')


class TestBaseFieldSerialized(TransactionCase):
    def test_ReadWrite(self):
        BaseFieldSerializedTestModel._build_model(self.registry, self.cr)
        self.env['base.field.serialized.test.model']._auto_init()
        record = self.env['base.field.serialized.test.model'].create(
            {'serialized': ['hello world']})
        self.assertEqual(record.serialized, ['hello world'])
        self.env.invalidate_all()
        self.assertEqual(record.serialized, ['hello world'])
        record.write({'serialized': {'hello': 'world'}})
        self.env.invalidate_all()
        self.assertEqual(record.serialized, {'hello': 'world'})
        record.write({'serialized': None})
        self.assertEqual(
            self.registry['base.field.serialized.test.model'].browse(
                self.cr, self.uid, record.id).serialized,
            {})
