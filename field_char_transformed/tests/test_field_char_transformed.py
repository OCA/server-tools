# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import SUPERUSER_ID, models
from openerp.tests.common import TransactionCase
from openerp.addons.field_char_transformed import FieldCharStripped


class StrippedTest(models.TransientModel):
    _name = 'test.field.char.stripped'

    name = FieldCharStripped()


class TestFieldCharTransformed(TransactionCase):
    def test_field_char_transformed(self):
        model = StrippedTest._build_model(self.registry, self.cr)
        model._prepare_setup(self.cr, SUPERUSER_ID, False)
        model._setup_base(self.cr, SUPERUSER_ID, False)
        model._setup_fields(self.cr, SUPERUSER_ID)
        model._auto_init(self.cr)
        record_id = model.create(
            self.cr,
            SUPERUSER_ID,
            {
                'name': '     hello     world    ',
            })
        self.cr.execute(
            'select name from %s where id=%%s' % model._table, (record_id,))
        self.assertEqual(self.cr.fetchall()[0][0], 'hello     world')
        record = model.browse(self.cr, SUPERUSER_ID, record_id)
        self.assertEqual(record.name, 'hello     world')
