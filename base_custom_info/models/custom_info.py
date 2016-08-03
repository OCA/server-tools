# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería S.L. - Sergio Teruel
# © 2015 Antiun Ingeniería S.L. - Carlos Dauden
# © 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from openerp import api, fields, models


class CustomInfo(models.AbstractModel):
    """Models that inherit this one will get custom information for free!

    They will probably want to declare a default model in the context of the
    :attr:`custom_info_template_id` field.

    See example in :mod:`res_partner`.
    """
    _description = "Inheritable abstract model to add custom info in any model"
    _name = "custom.info"

    custom_info_template_id = fields.Many2one(
        comodel_name='custom.info.template',
        domain=lambda self: [("model", "=", self._name)],
        string='Custom Information Template')
    custom_info_ids = fields.One2many(
        comodel_name='custom.info.value',
        inverse_name='res_id',
        domain=lambda self: [("model", "=", self._name)],
        context={"embed": True},
        auto_join=True,
        string='Custom Properties')

    @api.multi
    @api.onchange('custom_info_template_id')
    def _onchange_custom_info_template_id(self):
        new = [(5, False, False)]
        for prop in self.custom_info_template_id.property_ids:
            new += [(0, False, {
                "property_id": prop.id,
                "res_id": self.id,
                "model": self._name,
            })]
        self.custom_info_ids = new
        self.custom_info_ids._onchange_property_set_default_value()
        self.custom_info_ids._inverse_value()
        self.custom_info_ids._compute_value()

    # HACK https://github.com/OCA/server-tools/pull/492#issuecomment-237594285
    @api.multi
    def onchange(self, values, field_name, field_onchange):
        """Add custom info children values that will be probably changed."""
        subfields = ("category_id", "field_type", "required", "property_id",
                     "res_id", "model", "value", "value_str", "value_int",
                     "value_float", "value_bool", "value_id")
        for subfield in subfields:
            field_onchange.setdefault("custom_info_ids." + subfield, "")
        return super(CustomInfo, self).onchange(
            values, field_name, field_onchange)

    @api.multi
    def unlink(self):
        info_values = self.mapped('custom_info_ids')
        res = super(CustomInfo, self).unlink()
        if res:
            info_values.unlink()
        return res

    @api.multi
    @api.returns("custom.info.value")
    def get_custom_info_value(self, properties):
        """Get ``custom.info.value`` records for the given property."""
        return self.env["custom.info.value"].search([
            ("model", "=", self._name),
            ("res_id", "in", self.ids),
            ("property_id", "in", properties.ids),
        ])
