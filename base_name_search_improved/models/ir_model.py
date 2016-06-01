# -*- coding: utf-8 -*-
# © 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp import SUPERUSER_ID


class ModelExtended(models.Model):
    _inherit = 'ir.model'

    name_search_ids = fields.Many2many(
        'ir.model.fields',
        string='Name Search Fields')

    def _register_hook(self, cr, ids=None):

        def make_name_search():

            @api.model
            def name_search(self, name='', args=None,
                            operator='ilike', limit=100):
                # Regular name search
                res = name_search.origin(
                    self, name=name, args=args, operator=operator, limit=limit)

                allowed_ops = ['ilike', 'like', '=']
                if not res and operator in allowed_ops and self._rec_name:
                    # Support a list of fields to search on
                    model = self.env['ir.model'].search(
                        [('model', '=', str(self._model))])
                    other_names = model.name_search_ids.mapped('name')
                    # Try regular search on each additional search field
                    for rec_name in other_names:
                        domain = [(rec_name, operator, name)]
                        recs = self.search(domain, limit=limit)
                        if recs:
                            return recs.name_get()
                    # Try ordered word search on each of the search fields
                    for rec_name in [self._rec_name] + other_names:
                        domain = [(rec_name, operator, name.replace(' ', '%'))]
                        recs = self.search(domain, limit=limit)
                        if recs:
                            return recs.name_get()
                    # Try unordered word search on each of the search fields
                    for rec_name in [self._rec_name] + other_names:
                        domain = [(rec_name, operator, x)
                                  for x in name.split() if x]
                        recs = self.search(domain, limit=limit)
                        if recs:
                            return recs.name_get()
                return res
            return name_search

        if ids is None:
            ids = self.search(cr, SUPERUSER_ID, [])
        for model in self.browse(cr, SUPERUSER_ID, ids):
            Model = self.pool.get(model.model)
            if Model:
                Model._patch_method('name_search', make_name_search())
        return super(ModelExtended, self)._register_hook(cr)
