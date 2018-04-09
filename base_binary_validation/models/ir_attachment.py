# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).
from odoo import models, api, exceptions, _


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def create(self, values):
        rec = super().create(values)
        rec._validate_mimetype()
        return rec

    @api.multi
    def write(self, values):
        res = super().write(values)
        for rec in self:
            rec._validate_mimetype()
        return res

    def _validate_mimetype(self, allowed_mimetypes=None, raise_exception=True):
        wanted = self.env.context.get(
            'allowed_mimetypes', allowed_mimetypes) or []
        if wanted and self.mimetype not in wanted:
            if raise_exception:
                raise exceptions.ValidationError(_(
                    'Invalid file content for field `%s`.\n'
                    'Got: `%s`.\n'
                    'Allowed types: %s.'
                ) % (self.name, self.mimetype, ', '.join(wanted)))
            else:
                return {
                    'mimetype': self.mimetype,
                    'allowed': wanted,
                }
