# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from .field_char_transformed import FieldCharTransformed


class FieldCharStripped(FieldCharTransformed):
    def __init__(self, string=None, **kwargs):
        kwargs['transform'] = lambda x: x and x.strip() or x
        super(FieldCharStripped, self).__init__(string=string, **kwargs)
