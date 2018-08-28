# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class IrModelField(models.Model):
    _inherit = 'ir.model.fields'

    dependant_default = fields.Char(
        help='When set, defines a dependant function'
    )

    def _reflect_field_params(self, field):
        vals = super(IrModelField, self)._reflect_field_params(field)
        vals['dependant_default'] = getattr(field, 'dependant_default', None)
        return vals

    def _instanciate_attrs(self, field_data):
        attrs = super(IrModelField, self)._instanciate_attrs(field_data)
        if attrs and field_data.get('dependant_default'):
            attrs['dependant_default'] = field_data['dependant_default']
        return attrs
