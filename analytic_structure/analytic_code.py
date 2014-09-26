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
    _name = 'analytic.code'
    _description = u"Analytic Code"

    _parent_name = 'code_parent_id'
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

    def _read_disabled_per_company(
        self, cr, uid, ids, field_name, arg, context
    ):
        """Mark the code as disabled when it is in the blacklist (depending on
        the current user's company).
        """

        anc_obj = self.pool['analytic.code']
        user_obj = self.pool['res.users']

        company_id = user_obj.read(
            cr, uid, [uid], ['company_id'], context=context
        )[0]['company_id'][0]

        ret = {}

        for anc in anc_obj.browse(cr, uid, ids, context=context):
            blacklist = (company.id for company in anc.blacklist_ids)
            ret[anc.id] = company_id in blacklist

        return ret

    def _write_disabled_per_company(
        self, cr, uid, anc_id, field_name, field_value, arg, context
    ):
        """Update the blacklist depending on the current user's company.
        """

        anc_obj = self.pool['analytic.code']
        user_obj = self.pool['res.users']

        company_id = user_obj.read(
            cr, uid, [uid], ['company_id'], context=context
        )[0]['company_id'][0]

        anc = anc_obj.browse(cr, uid, anc_id, context=context)
        blacklist = (company.id for company in anc.blacklist_ids)

        to_write = None
        if field_value and company_id not in blacklist:
            to_write = [(4, company_id)]  # Link.
        elif not field_value and company_id in blacklist:
            to_write = [(3, company_id)]  # Unlink.

        if to_write:
            anc_obj.write(
                cr, uid, [anc_id], {'blacklist_ids': to_write}, context=context
            )

        return True

    def _search_disabled_per_company(
        self, cr, uid, model_again, field_name, criterion, context
    ):
        """Update the domain to take the blacklist into account (depending on
        the current user's company).
        """

        user_obj = self.pool['res.users']

        company_id = user_obj.read(
            cr, uid, [uid], ['company_id'], context=context
        )[0]['company_id'][0]

        # We assume the criterion was "disabled_per_company = False".
        dom = [
            '|',
            ('blacklist_ids', '=', False),
            ('blacklist_ids', '!=', company_id),  # Not blacklists_ids.id!
        ]
        if criterion[0][2] is True:
            dom = ['!'] + dom
        return dom

    _columns = {
        'name': fields.char(
            u"Name",
            size=128,
            translate=config.get_misc('analytic', 'translate', False),
            required=True,
        ),
        'nd_id': fields.many2one(
            'analytic.dimension',
            string=u"Dimension",
            ondelete='cascade',
            required=True,
        ),

        'active': fields.boolean(
            u"Active",
            help=(
                u"Determines whether an analytic code is in the referential."
            ),
        ),
        'view_type': fields.boolean(
            u"View type",
            help=(
                u"Determines whether an analytic code is not selectable (but "
                u"still in the referential)."
            ),
        ),
        'blacklist_ids': fields.many2many(
            'res.company',
            'analytic_code_company_rel',
            'code_id',
            'company_id',
            u"Blacklist",
            help=u"Companies the code is hidden in.",
        ),
        'disabled_per_company': fields.function(
            _read_disabled_per_company,
            fnct_inv=_write_disabled_per_company,
            fnct_search=_search_disabled_per_company,
            method=True,
            type='boolean',
            store=False,  # Not persistent as it depends on the company.
            string=u"Disabled in my company",
            help=(
                u"Determines whether an analytic code is disabled for the "
                u"current company."
            ),
        ),

        'nd_name': fields.related(
            'nd_id',
            'name',
            type='char',
            string=u"Dimension Name",
            store=False
        ),
        'description': fields.char(
            u"Description",
            size=512,
            translate=config.get_misc('analytic', 'translate', False),
        ),
        'code_parent_id': fields.many2one(
            'analytic.code',
            u"Parent Code",
            select=True,
            ondelete='restrict',
        ),
        'child_ids': fields.one2many(
            'analytic.code',
            'code_parent_id',
            u"Child Codes",
        ),
        'parent_left': fields.integer(u"Left parent", select=True),
        'parent_right': fields.integer(u"Right parent", select=True),
    }

    _defaults = {
        'active': lambda *a: True,
        'view_type': lambda *a: False,
        'disabled_per_company': lambda *a: False,
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
