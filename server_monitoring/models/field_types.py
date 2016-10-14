# -*- coding: utf-8 -*-
# Author: Alexandre Fayolle
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, osv


class Bigint(fields.Integer):
    type = 'bigint'


class OsvBigint(osv.fields.integer):
    _type = 'int8'


fields.Bigint = Bigint
osv.fields.bigint = OsvBigint

models.FIELDS_TO_PGTYPES[OsvBigint] = 'int8'
