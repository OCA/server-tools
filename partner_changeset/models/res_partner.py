# -*- coding: utf-8 -*-
# Copyright 2015-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    changeset_ids = fields.One2many(comodel_name='res.partner.changeset',
                                    inverse_name='partner_id',
                                    string='Changesets',
                                    readonly=True)
    count_pending_changesets = fields.Integer(
        string='Changes',
        compute='_count_pending_changesets',
        search='_search_count_pending_changesets')

    @api.one
    @api.depends('changeset_ids', 'changeset_ids.state')
    def _count_pending_changesets(self):
        changesets = self.changeset_ids.filtered(
            lambda rev: rev.state == 'draft' and rev.partner_id == self
        )
        self.count_pending_changesets = len(changesets)

    @api.multi
    def write(self, values):
        if self.env.context.get('__no_changeset'):
            return super(ResPartner, self).write(values)
        else:
            changeset_model = self.env['res.partner.changeset']
            for record in self:
                local_values = changeset_model.add_changeset(record, values)
                super(ResPartner, record).write(local_values)
        return True

    def _search_count_pending_changesets(self, operator, value):
        if operator not in ('=', '!=', '<', '<=', '>', '>=', 'in', 'not in'):
            return []
        query = ("SELECT p.id "
                 "FROM res_partner p "
                 "INNER JOIN res_partner_changeset r ON r.partner_id = p.id "
                 "WHERE r.state = 'draft' "
                 "GROUP BY p.id "
                 "HAVING COUNT(r.id) %s %%s ") % operator
        self.env.cr.execute(query, (value,))
        ids = [row[0] for row in self.env.cr.fetchall()]
        return [('id', 'in', ids)]
