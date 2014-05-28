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
from openerp.tools import config


class analytic_code(osv.Model):
    _name = "analytic.code"
    _description = u"Analytic Code"

    _parent_name = 'code_parent_id'
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

    _columns = dict(
        name=fields.char(
            "Name",
            size=128,
            translate=config.get_misc('analytic', 'translate', False),
            required=True,
        ),
        nd_id=fields.many2one(
            "analytic.dimension",
            string="Dimension",
            ondelete="cascade",
            required=True,
        ),
        active=fields.boolean('Active'),
        nd_name=fields.related('nd_id', 'name', type="char",
                               string="Dimension Name", store=False),
        description=fields.char(
            'Description',
            size=512,
            translate=config.get_misc('analytic', 'translate', False),
        ),
        code_parent_id=fields.many2one(
            'analytic.code',
            u"Parent Code",
            select=True,
            ondelete='restrict',
        ),
        child_ids=fields.one2many(
            'analytic.code',
            'code_parent_id',
            u"Child Codes",
        ),
        parent_left=fields.integer(u"Left parent", select=True),
        parent_right=fields.integer(u"Right parent", select=True),
    )

    _defaults = {
        'active': 1,
    }

    _constraints = [
        # very useful base class constraint
        (
            osv.Model._check_recursion,
            u"Error ! You can not create recursive analytic codes.",
            ['parent_id']
        ),
    ]

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        if isinstance(ids, (int, long)):
            ids = [ids]

        reads = self.read(cr, uid, ids,
                          [
                              'name',
                              'description'
                          ], context=context
                          )
        res = []
        for record in reads:
            name = record['name']
            if record['description']:
                name = name + ' ' + record['description']
            res.append((record['id'], name))

        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []

        if not context:
            context = {}

        ids = []
        if name:
            ids.extend(
                self.search(cr, uid, [
                    '|',
                    ('name', operator, name),
                    ('description', operator, name)
                ] + args, limit=limit, context=context,
                )
            )
            return self.name_get(cr, uid, ids)
        else:
            return super(analytic_code, self).name_search(
                cr, uid, name=name, args=args, operator=operator,
                context=context, limit=limit)
