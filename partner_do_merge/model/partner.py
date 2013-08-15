# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import openerp
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.tools.yaml_import import is_comment


class res_partner(osv.Model):
    _description = 'Partner'
    _inherit = "res.partner"

    def _commercial_partner_compute(self, cr, uid, ids, name, args,
                                    context=None):
        """ Returns the partner that is considered the commercial
        entity of this partner. The commercial entity holds the master data
        for all commercial fields (see :py:meth:`~_commercial_fields`) """
        result = dict.fromkeys(ids, False)
        for partner in self.browse(cr, uid, ids, context=context):
            current_partner = partner
            while not current_partner.is_company and current_partner.parent_id:
                current_partner = current_partner.parent_id
            result[partner.id] = current_partner.id
        return result

    def _display_name_compute(self, cr, uid, ids, name, args, context=None):
        return dict(self.name_get(cr, uid, ids, context=context))

    # indirections to avoid passing a copy of the overridable method when
    # declaring the function field
    _display_name = lambda self, *args, **kwargs: \
        self._display_name_compute(*args, **kwargs)

    _display_name_store_triggers = {
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.search(cr, uid, [(
                                    'id', 'child_of', ids)]),
                        ['parent_id', 'is_company', 'name'], 10)
    }

    _order = "display_name"
    _columns = {
        'display_name': fields.function(_display_name, type='char',
                                        string='Name',
                                        store=_display_name_store_triggers),
        'id': fields.integer('Id', readonly=True),
        'create_date': fields.datetime('Create Date', readonly=True),
        'partner_merged_ids' : fields.many2many('res.partner',\
            'partners_mergeds', 'partner_active', 'partner_id', 'Relation '\
            'with partner merged', domain=['|', ('active','=',True), (\
            'active','=',False)], readonly=True)


    }

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id and not record.is_company:
                name = "%s, %s" % (record.parent_id.name, name)
            if context.get('show_address'):
                name = name + "\n" + \
                    self._display_address(cr, uid, record,
                                          without_company=True,
                                          context=context)
                name = name.replace('\n\n', '\n')
                name = name.replace('\n\n', '\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            res.append((record.id, name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]
            query_args = {'name': search_name}
            limit_str = ''
            if limit:
                limit_str = ' limit %(limit)s'
                query_args['limit'] = limit
            cr.execute('''SELECT partner.id FROM res_partner partner
                          LEFT JOIN res_partner company
                          ON partner.parent_id = company.id
                          WHERE partner.email ''' + operator + ''' %(name)s OR
                                partner.display_name ''' + operator +
                       ' %(name)s ' + limit_str, query_args)
            ids = map(lambda x: x[0], cr.fetchall())
            ids = self.search(cr, uid, [('id', 'in', ids)] + args,
                              limit=limit, context=context)
            if ids:
                return self.name_get(cr, uid, ids, context)
        return super(res_partner, self).name_search(cr, uid, name, args,
                                                    operator=operator,
                                                    context=context,
                                                    limit=limit)
