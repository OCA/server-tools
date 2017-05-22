# -*- coding: utf-8 -*-
# © 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class BaseModelPatch(models.Model):
    _name = "base.model.patch"
    _auto = False

    def init(self, cr):

        base_model = BaseModelPatch.__bases__[0]
        upgrade = lambda self, value, args, offset=0, limit=None, \
            order=None, count=False: value if count else self.browse(value)
        downgrade = lambda self, value, args, offset=0, limit=None, \
            order=None, count=False: value if count else value.ids

        @api.returns('self', upgrade=upgrade, downgrade=downgrade)
        def new_search(self, cr, user, args, offset=0, limit=None,
                       order=None, context=None, count=False):
            for i, cond in enumerate(args):
                # fuzzy search: replace spaces with wildcards
                if len(cond) == 3 and cond[1] == 'ilike':
                    args[i] = cond[0], cond[1], cond[2].replace(' ', '%')
            return new_search.origin(self, cr, user, args, offset, limit,
                                     order, context, count)

        base_model._patch_method('search', new_search)
