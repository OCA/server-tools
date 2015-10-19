# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 XCG Consulting (www.xcg-consulting.fr)
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
from openerp.tools import config

from openerp.addons.base_model_metaclass_mixin import BaseModelMetaclassMixin


class _DimensionMeta(BaseModelMetaclassMixin):

    def __new__(cls, name, bases, nmspc):

        size = int(config.get_misc('analytic', 'analytic_size', 5))
        for n in xrange(1, size + 1):
            nmspc['ns{}_id'.format(n)] = fields.One2many(
                'analytic.structure',
                'nd_id',
                "Generated Subset of Structures",
                domain=[('ordering', '=', n)],
                auto_join=True,
            )
        return super(_DimensionMeta, cls).__new__(cls, name, bases, nmspc)


class AnalyticDimension(models.Model):

    __metaclass__ = _DimensionMeta
    _name = 'analytic.dimension'
    _description = u"Analytic Dimension"

    name = fields.Char(
        string=u"Name",
        size=128,
        translate=config.get_misc('analytic', 'translate', False),
        required=True,
    )

    nc_ids = fields.One2many(
        comodel_name='analytic.code',
        inverse_name='nd_id',
        string=u"Codes")

    ns_id = fields.One2many(
        comodel_name='analytic.structure',
        inverse_name='nd_id',
        string=u"Structures")

    _sql_constraints = [
        ('unique_name', 'unique(name)', u"Name must be unique"),
    ]
