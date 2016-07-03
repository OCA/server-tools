# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class BaseEncryptedFieldPatchBaseModel(models.BaseModel):
    _name = 'base.encrypted.field.patch.base.model'
    _description = 'Patch methods on BaseModel for all existing models'
    _inherit = 'base.patch.models.mixin'

    def fields_get(self, cr, user, allfields=None, context=None,
                   write_access=True, attributes=None):
        # this is called with positional parameter by res.users, so detecting
        # v8 api doesn't work
        result = super(BaseEncryptedFieldPatchBaseModel, self).fields_get(
            cr, user, allfields=allfields, context=context,
            write_access=write_access, attributes=attributes)
        for field_name, field_desc in result.iteritems():
            self._base_encrypted_fields_inject_field_description(
                cr, user, field_name, field_desc, context=context)
        return result

    @api.model
    def _base_encrypted_fields_inject_field_description(self, field_name,
                                                        field_desc):
        if field_desc.get('store') and\
                field_desc.get('type') in ['text', 'html'] and\
                not field_desc.get('size'):
            field_desc.setdefault('encryptable', True)
