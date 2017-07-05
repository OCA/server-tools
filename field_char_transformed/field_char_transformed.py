# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields
from openerp.osv import fields as low_level_fields


class ColumnCharTransformed(low_level_fields.char):
    def _transform(self, value):
        return low_level_fields._symbol_set_char(self, self.transform(value))

    def __init__(self, string="unknown", size=None, **args):
        super(ColumnCharTransformed, self).__init__(
            string=string, size=size, **args
        )
        if self.transform:
            self._symbol_f = self._symbol_set_char = self._transform
            self._symbol_set = (self._symbol_c, self._symbol_f)


class FieldCharTransformed(fields.Char):
    _slots = {
        # a callable receiving a value and returning its result
        'transform': None,
    }

    def convert_to_read(self, value, use_name_get=True):
        result = super(FieldCharTransformed, self).convert_to_read(
            value, use_name_get=use_name_get)
        if self.transform:
            return self.transform(result)
        return result

    def convert_to_write(self, value, target=None, fnames=None):
        result = super(FieldCharTransformed, self).convert_to_write(
            value, target=target, fnames=fnames)
        if self.transform:
            return self.transform(result)
        return result

    def to_column(self):
        result = super(FieldCharTransformed, self).to_column()
        if result and isinstance(result, low_level_fields.char):
            result = ColumnCharTransformed(
                transform=self.transform, **result._args)
        return result
