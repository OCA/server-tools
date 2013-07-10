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


class analytic_code(osv.Model):
    _name = "analytic.code"

    _columns = dict(
        name=fields.char("Name", size=128, translate=True, required=True),
        nd_id=fields.many2one(
            "analytic.dimension", "Dimensions", ondelete="cascade"),
        active=fields.boolean('Active'),
        nd_name=fields.related('nd_id', 'name', type="char",
                               string="Dimension Name", store=False),
        description=fields.char('Description', size=512),
    )
    _defaults = {
        'active': 1,
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'description'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['description']:
                name = name + ' ' + record['description']
                res.append((record['id'], name))
        return res
