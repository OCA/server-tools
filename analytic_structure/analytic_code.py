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

from openerp import api, models, fields
from openerp.tools import config


class AnalyticCode(models.Model):
    _name = 'analytic.code'
    _description = u"Analytic Code"

    _parent_name = 'code_parent_id'
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

    @api.depends('blacklist_ids')
    def _read_disabled_per_company(self):
        """Mark the code as disabled when it is in the blacklist (depending on
        the current user's company).
        """

        company_id = self.env.user.company_id.id

        for anc in self:
            blacklist = (company.id for company in anc.blacklist_ids)
            anc.disabled_per_company = company_id in blacklist

    def _write_disabled_per_company(self):
        """Update the blacklist depending on the current user's company.
        """

        company_id = self.env.user.company_id.id

        for anc in self:
            blacklist = (company.id for company in anc.blacklist_ids)

            to_write = None
            if anc.disabled_per_company and company_id not in blacklist:
                to_write = [(4, company_id)]  # Link.
            elif not anc.disabled_per_company and company_id in blacklist:
                to_write = [(3, company_id)]  # Unlink.

            if to_write:
                anc.write({'blacklist_ids': to_write})

        return True

    def _search_disabled_per_company(self, operator, value):
        """Update the domain to take the blacklist into account (depending on
        the current user's company).
        """

        company_id = self.env.user.company_id.id

        # We assume the criterion was "disabled_per_company = False".
        dom = [
            '|',
            ('blacklist_ids', '=', False),
            ('blacklist_ids', '!=', company_id),  # Not blacklists_ids.id!
        ]
        if value is True:
            dom = ['!'] + dom
        return dom

    name = fields.Char(
        u"Name",
        size=128,
        translate=config.get_misc('analytic', 'translate', False),
        required=True,
    )
    nd_id = fields.Many2one(
        'analytic.dimension',
        string=u"Dimension",
        ondelete='cascade',
        required=True,
    )

    active = fields.Boolean(
        u"Active",
        help=(
            u"Determines whether an analytic code is in the referential."
        ),
        default = lambda *a: True
    )
    view_type = fields.Boolean(
        u"View type",
        help=(
            u"Determines whether an analytic code is not selectable (but "
            u"still in the referential)."
        ),
        default = lambda *a: False
    )
    blacklist_ids = fields.Many2many(
        'res.company',
        'analytic_code_company_rel',
        'code_id',
        'company_id',
        u"Blacklist",
        help=u"Companies the code is hidden in.",
    )
    disabled_per_company = fields.Boolean(
        string=u"Disable in my company",
        compute=_read_disabled_per_company,
        inverse=_write_disabled_per_company,
        search=_search_disabled_per_company,
        help=(
            u"Determines whether an analytic code is disabled for the "
            u"current company."
        ),
        default = lambda *a: False
    )

    nd_name = fields.Char(
        related='nd_id.name',
        string=u"Dimension Name",
        store=False
    )
    description = fields.Char(
        u"Description",
        size=512,
        translate=config.get_misc('analytic', 'translate', False),
    )
    code_parent_id = fields.Many2one(
        'analytic.code',
        u"Parent Code",
        select=True,
        ondelete='restrict',
    )
    child_ids = fields.One2many(
        'analytic.code',
        'code_parent_id',
        u"Child Codes",
    )
    parent_left = fields.Integer(u"Left parent", select=True)
    parent_right = fields.Integer(u"Right parent", select=True)

    _constraints = [
        # very useful base class constraint
        (
            models.Model._check_recursion,
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

    def name_search(
        self, cr, uid, name, args=None, operator='ilike', context=None,
        limit=100
    ):
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
            return super(AnalyticCode, self).name_search(
                cr, uid, name=name, args=args, operator=operator,
                context=context, limit=limit
            )
