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
    dirty_templates = fields.Boolean(
        compute="_compute_dirty_templates",
    )

    # HACK https://github.com/odoo/odoo/pull/11042
    @api.model
    def create(self, vals):
        res = super(CustomInfo, self).create(vals)
        if not self.env.context.get("filling_templates"):
            res.filtered(
                "dirty_templates").action_custom_info_templates_fill()
        return res

    # HACK https://github.com/odoo/odoo/pull/11042
    @api.multi
    def write(self, vals):
        res = super(CustomInfo, self).write(vals)
        if not self.env.context.get("filling_templates"):
            self.filtered(
                "dirty_templates").action_custom_info_templates_fill()
        return res

    @api.multi
    def unlink(self):
        info_values = self.mapped('custom_info_ids')
        res = super(CustomInfo, self).unlink()
        if res:
            info_values.unlink()
        return res

    @api.one
    @api.depends("custom_info_template_id",
                 "custom_info_ids.value_id.template_id")
    def _compute_dirty_templates(self):
        """Know if you need to reload the templates."""
        expected_properties = self.all_custom_info_templates().mapped(
            "property_ids")
        actual_properties = self.mapped("custom_info_ids.property_id")
        self.dirty_templates = expected_properties != actual_properties

    @api.multi
    @api.returns("custom.info.value")
    def get_custom_info_value(self, properties):
        """Get ``custom.info.value`` records for the given property."""
        return self.env["custom.info.value"].search([
            ("model", "=", self._name),
            ("res_id", "in", self.ids),
            ("property_id", "in", properties.ids),
        ])

    @api.multi
    def all_custom_info_templates(self):
        """Get all custom info templates involved in these owners."""
        return (self.mapped("custom_info_template_id") |
                self.mapped("custom_info_ids.value_id.template_id"))

    @api.multi
    def action_custom_info_templates_fill(self):
        """Fill values with enabled custom info templates."""
        recursive_owners = self
        for owner in self.with_context(filling_templates=True):
            values = owner.custom_info_ids
            tpls = owner.all_custom_info_templates()
            props_good = tpls.mapped("property_ids")
            props_enabled = owner.mapped("custom_info_ids.property_id")
            to_add = props_good - props_enabled
            to_rm = props_enabled - props_good
            # Remove remaining properties
            # HACK https://github.com/odoo/odoo/pull/13480
            values.filtered(lambda r: r.property_id in to_rm).unlink()
            values = values.exists()
            # Add new properties
            for prop in to_add:
                newvalue = values.new({
                    "property_id": prop.id,
                    "res_id": owner.id,
                })
                newvalue._onchange_property_set_default_value()
                # HACK https://github.com/odoo/odoo/issues/13076
                newvalue._inverse_value()
                newvalue._compute_value()
                values |= newvalue
            owner.custom_info_ids = values
            # Default values implied new templates? Then this is recursive
            if owner.all_custom_info_templates() == tpls:
                recursive_owners -= owner
        # Changes happened under a different environment; update own
        self.invalidate_cache()
        if recursive_owners:
            return recursive_owners.action_custom_info_templates_fill()
