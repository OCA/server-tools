# Copyright 2015 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2015 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, fields, models


class CustomInfo(models.AbstractModel):
    """Models that inherit from this one will get custom information for free!

    They will probably want to declare a default model in the context of the
    :attr:`custom_info_template_id` field.

    See example in :mod:`res_partner`.
    """

    _description = "Inheritable abstract model to add custom info in any model"
    _name = "custom.info"

    custom_info_template_id = fields.Many2one(
        comodel_name="custom.info.template",
        domain=lambda self: [("model", "=", self._name)],
        string="Custom Information Template",
    )
    custom_info_ids = fields.One2many(
        comodel_name="custom.info.value",
        inverse_name="res_id",
        domain=lambda self: [("model", "=", self._name)],
        auto_join=True,
        string="Custom Properties",
    )

    # HACK: Until https://github.com/odoo/odoo/pull/10557 is merged
    # https://github.com/OCA/server-tools/pull/492#issuecomment-237594285
    def onchange(self, values, field_name, field_onchange):  # pragma: no cover
        x2many_field = "custom_info_ids"
        if x2many_field in field_onchange:
            subfields = getattr(self, x2many_field)._fields.keys()
            for subfield in subfields:
                field_onchange.setdefault(
                    "{}.{}".format(x2many_field, subfield),
                    "",
                )
        return super().onchange(values, field_name, field_onchange)

    @api.onchange("custom_info_template_id")
    def _onchange_custom_info_template_id(self):
        tmpls = self.all_custom_info_templates()
        props_good = tmpls.mapped("property_ids")
        props_enabled = self.mapped("custom_info_ids.property_id")
        to_add = props_good - props_enabled
        to_remove = props_enabled - props_good
        values = self.custom_info_ids
        values = values.filtered(lambda r: r.property_id not in to_remove)
        for prop in to_add.sorted():
            vals = {
                "property_id": prop.id,
                "res_id": self.id,
            }
            if prop.default_value:
                if prop.field_type != "id":
                    vals["value_%s" % prop.field_type] = prop.default_value
                else:
                    vals["value_id"] = (
                        self.env["custom.info.option"]
                        .search(
                            [
                                ("property_ids", "=", prop.id),
                                ("name", "=", prop.default_value),
                            ],
                            limit=1,
                        )
                        .id
                    )
            newvalue = self.custom_info_ids.new(vals)
            newvalue._onchange_property_set_default_value()
            newvalue._compute_value()
            values += newvalue
        self.custom_info_ids = values
        # Default values implied new templates? Then this is recursive
        if self.all_custom_info_templates() != tmpls:
            self._onchange_custom_info_template_id()

    def unlink(self):
        """Remove linked custom info this way, as can't be handled
        automatically.
        """
        info_values = self.mapped("custom_info_ids")
        res = super().unlink()
        if res:
            info_values.unlink()
        return res

    @api.returns("custom.info.value")
    def get_custom_info_value(self, properties):
        """Get ``custom.info.value`` records for the given property."""
        return self.env["custom.info.value"].search(
            [
                ("model", "=", self._name),
                ("res_id", "in", self.ids),
                ("property_id", "in", properties.ids),
            ]
        )

    def all_custom_info_templates(self):
        """Get all custom info templates involved in these owners."""
        return self.mapped("custom_info_template_id") | self.mapped(
            "custom_info_ids.value_id.template_id"
        )

    # TODO: Revisar
    @api.model
    def get_views(self, views, options=None):
        """Adapt the label of the dummy search field

        Ensure the technical name does not show up in the Custom Filter
        fields list (while still showing up in the Export widget)
        """
        result = super().get_views(views, options=options)
        result["models"]["custom.info.value"] = self.env[
            "custom.info.value"
        ].fields_get(allfields=[], attributes=self._get_view_field_attributes())
        # if "date_range_search_id" in result["models"][self._name]:
        #     result["models"][self._name]["date_range_search_id"]["string"] = _("Period")
        return result
