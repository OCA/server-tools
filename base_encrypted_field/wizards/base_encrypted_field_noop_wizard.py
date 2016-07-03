# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class BaseEncryptedFieldNoopWizard(models.AbstractModel):
    _name = 'base.encrypted.field.noop.wizard'
    _description = 'A wizard that does nothing'

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        return True

    @api.model
    @api.returns('self', lambda x: x.id)
    def create(self, values):
        return self.browse([42])

    @api.multi
    def button_save(self):
        return {'type': 'ir.actions.act_window.close'}

    @api.multi
    def read(self, fields_list=None, load='_classic_read'):
        return [
            {
                name: field.convert_to_read(field.null(self.env))
                if name != 'id' else this.id
                for name, field
                in self._fields.iteritems()
            }
            for this in self
        ]

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        return [42] if not count else 1
