# -*- coding: utf-8 -*-
# © 2016 initOS GmbH http://www.initos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class ModelExtended(models.Model):
    _inherit = 'ir.model'

    def _register_hook(self, cr):
        for m in self.pool.models.itervalues():
            if getattr(m, '_disable_field_translations', False):
                for f in m._fields.itervalues():
                    if hasattr(f, 'translate') and f.translate:
                        f.translate = False
                    if getattr(f, 'column', False) and f.column.translate:
                        f.column.translate = False

        return super(ModelExtended, self)._register_hook(cr)
