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
from openerp.tools.translate import _


ORDER_SELECTION = (
    ('1', 'Analysis 1'),
    ('2', 'Analysis 2'),
    ('3', 'Analysis 3'),
    ('4', 'Analysis 4'),
    ('5', 'Analysis 5')
)

class analytic_structure(osv.Model):
    _name = "analytic.structure"

    _columns = dict(
        model_name=fields.char("Object", size=128, required=True, select="1"),
        nd_id=fields.many2one(
            "analytic.dimension", "Related Dimension", ondelete="restrict", required=True, select="1"),
        ordering=fields.selection(ORDER_SELECTION, 'Analysis slot', required=True),
    )
    _sql_constraints = [
        ('unique_ordering', 'unique(model_name,ordering)', 'One dimension per Analysis slot per object'),
    ]
