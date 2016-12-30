# -*- coding: utf-8 -*-
# Copyright 2015-2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class IrExports(models.Model):
    _inherit = 'ir.exports'

    name = fields.Char(required=True)
    resource = fields.Char(
        required=False,
        readonly=True,
        help="Model's technical name.")
    model_id = fields.Many2one(
        "ir.model",
        "Model",
        store=True,
        domain=[("transient", "=", False)],
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
    @api.onchange("model_id")
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
        """Check required values when creating the record.

        Odoo's export dialog populates ``resource``, while this module's new
        form populates ``model_id``. At least one of them is required to
        trigger the methods that fill up the other, so this should fail if
        one is missing.
        """
        if not any(f in vals for f in {"model_id", "resource"}):
            raise ValidationError(_("You must supply a model or resource."))
        return super(IrExports, self).create(vals)
