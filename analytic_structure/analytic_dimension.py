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

from openerp.osv import fields, osv
from openerp.addons.oemetasl import OEMetaSL
from openerp.tools import config


class _dimension_meta(OEMetaSL):

    def __new__(cls, name, bases, nmspc):

        columns = nmspc['_columns']
        size = int(config.get_misc('analytic', 'analytic_size', 5))
        for n in xrange(1, size + 1):
            columns['ns{}_id'.format(n)] = fields.one2many(
                'analytic.structure',
                'nd_id',
                "Generated Subset of Structures",
                domain=[('ordering', '=', n)],
                auto_join=True,
            )
        return super(_dimension_meta, cls).__new__(cls, name, bases, nmspc)


class analytic_dimension(osv.Model):

    __metaclass__ = _dimension_meta
    _name = 'analytic.dimension'
    _description = u"Analytic Dimension"

    _columns = {
        'name': fields.char(
            u"Name",
            size=128,
            translate=config.get_misc('analytic', 'translate', False),
            required=True,
        ),
        'validated': fields.boolean(u"Validated"),
        'nc_ids': fields.one2many('analytic.code', 'nd_id', u"Codes"),
        'ns_id': fields.one2many('analytic.structure', 'nd_id', u"Structures"),
    }

    _sql_constraints = [
        ('unique_name', 'unique(name)', u"Name must be unique"),
    ]
