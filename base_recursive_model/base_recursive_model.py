# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Buron. Copyright Yannick Buron
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm, osv


class BaseRecursiveModel(orm.AbstractModel):

    """
    Abstract model which can be inherited for model
    which need a parent-children relation
    """

    def name_get(self, cr, uid, ids, context=None):
        """
        Return the categories' display name,
        including their direct parent by default.
        """
        if context is None:
            context = {}
        if context.get('category_display') == 'short':
            return super(BaseRecursiveModel, self).name_get(
                cr, uid, ids, context=context
            )
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(
            cr, uid, ids, ['name', 'parent_id', 'sequence'], context=context
        )
        res = []
        for record in reads:
            if context.get('path_with_sequence'):
                name = str(record['sequence']) + ' ' + record['name']
            else:
                name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    def name_search(
            self, cr, uid, name, args=None, operator='ilike',
            context=None, limit=100
    ):
        """
        Search all category which contain name
        in their own name or in their parents
        """
        if args is None:
            args = []
        if context is None:
            context = {}
        if name:
            name = name.split(' / ')[-1]
            ids = self.search(
                cr, uid, [('name', operator, name)] + args,
                limit=limit, context=context
            )
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _name = 'base.recursive.model'

    _columns = {
        'complete_name': fields.function(
            _name_get_fnc, type="char", string='Full Name', store=True
        ),
        'parent_left': fields.integer('Left parent', select=True),
        'parent_right': fields.integer('Right parent', select=True),
    }
    _constraints = [
        (
            osv.osv._check_recursion,
            'Error! You can not create recursive categories.', ['parent_id']
        )
    ]
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_left'
