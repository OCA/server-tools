# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class IrExports(models.Model):
    _inherit = 'ir.exports'

    name = fields.Char(required=True)
    resource = fields.Char(
        required=True,
        readonly=True,
        help="Model's technical name.")
    model_id = fields.Many2one(
        "ir.model",
        "Model",
        required=True,
        store=True,
        domain=[("osv_memory", "=", False)],
        compute="_compute_model_id",
        inverse="_inverse_model_id",
        help="Database model to export.")

    @api.multi
    @api.depends("resource")
    def _compute_model_id(self):
        """Get the model from the resource."""
        for s in self:
            s.model_id = self._get_model_id(s.resource)

    @api.multi
    def _inverse_model_id(self):
        """Get the resource from the model."""
        for s in self:
            s.resource = s.model_id.model

    @api.multi
    @api.onchange("resource")
    def _onchange_resource(self):
        """Void fields if model is changed in a view."""
        for s in self:
            s.export_fields = False

    @api.model
    def _get_model_id(self, resource):
        """Return a model object from its technical name.

        :param str resource:
            Technical name of the model, like ``ir.model``.
        """
        return self.env["ir.model"].search([("model", "=", resource)])

    @api.model
    def create(self, vals):
        """Add new required value when missing.

        This is required because this model is created from a QWeb wizard view
        that does not populate ``model_id``, and it is easier to hack here than
        in the view.
        """
        vals.setdefault("model_id",
                        self._get_model_id(vals.get("resource")).id)
        return super(IrExports, self).create(vals)
