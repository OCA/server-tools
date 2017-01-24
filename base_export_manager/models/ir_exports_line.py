# -*- coding: utf-8 -*-
# Copyright 2015 Antiun Ingeniería S.L. - Antonio Espinosa
# Copyright 2015-2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions
from odoo.tools.translate import _


class IrExportsLine(models.Model):
    _inherit = 'ir.exports.line'
    _order = 'sequence,id'

    name = fields.Char(
        required=False,
        readonly=True,
        store=True,
        compute="_compute_name",
        inverse="_inverse_name",
        help="Field's technical name.")
    field1_id = fields.Many2one(
        "ir.model.fields",
        "First field",
        domain="[('model_id', '=', model1_id)]")
    field2_id = fields.Many2one(
        "ir.model.fields",
        "Second field",
        domain="[('model_id', '=', model2_id)]")
    field3_id = fields.Many2one(
        "ir.model.fields",
        "Third field",
        domain="[('model_id', '=', model3_id)]")
    field4_id = fields.Many2one(
        "ir.model.fields",
        "Fourth field",
        domain="[('model_id', '=', model4_id)]")
    model1_id = fields.Many2one(
        "ir.model",
        "First model",
        readonly=True,
        default=lambda self: self._default_model1_id(),
        related="export_id.model_id")
    model2_id = fields.Many2one(
        "ir.model",
        "Second model",
        compute="_compute_model2_id")
    model3_id = fields.Many2one(
        "ir.model",
        "Third model",
        compute="_compute_model3_id")
    model4_id = fields.Many2one(
        "ir.model",
        "Fourth model",
        compute="_compute_model4_id")
    sequence = fields.Integer()
    label = fields.Char(
        compute="_compute_label")

    @api.model
    def _default_model1_id(self):
        """Default model depending on context."""
        return self.env.context.get("default_model1_id", False)

    @api.multi
    @api.depends("field1_id", "field2_id", "field3_id", "field4_id")
    def _compute_name(self):
        """Get the name from the selected fields."""
        for one in self:
            name = "/".join((one.field_n(num).name for num in range(1, 5)
                             if one.field_n(num)))
            if name != one.name:
                one.name = name

    @api.multi
    @api.depends("field1_id")
    def _compute_model2_id(self):
        """Get the related model for the second field."""
        IrModel = self.env["ir.model"]
        for one in self:
            one.model2_id = (
                one.field1_id.ttype and
                "2" in one.field1_id.ttype and
                IrModel.search([("model", "=", one.field1_id.relation)]))

    @api.multi
    @api.depends("field2_id")
    def _compute_model3_id(self):
        """Get the related model for the third field."""
        IrModel = self.env["ir.model"]
        for one in self:
            one.model3_id = (
                one.field2_id.ttype and
                "2" in one.field2_id.ttype and
                IrModel.search([("model", "=", one.field2_id.relation)]))

    @api.multi
    @api.depends("field3_id")
    def _compute_model4_id(self):
        """Get the related model for the third field."""
        IrModel = self.env["ir.model"]
        for one in self:
            one.model4_id = (
                one.field3_id.ttype and
                "2" in one.field3_id.ttype and
                IrModel.search([("model", "=", one.field3_id.relation)]))

    @api.multi
    @api.depends('name')
    def _compute_label(self):
        """Column label in a user-friendly format and language."""
        for one in self:
            parts = list()
            for num in range(1, 5):
                field = one.field_n(num)
                if not field:
                    break
                # Translate label if possible
                try:
                    parts.append(
                        one.env[one.model_n(num).model]._fields[field.name]
                        .get_description(one.env)["string"])
                except KeyError:
                    # No human-readable string available, so empty this
                    return
            one.label = ("%s (%s)" % ("/".join(parts), one.name)
                         if parts and one.name else False)

    @api.multi
    def _inverse_name(self):
        """Get the fields from the name."""
        for one in self:
            # Field names can have up to only 4 indentation levels
            parts = one.name.split("/")
            if len(parts) > 4:
                raise exceptions.ValidationError(
                    _("It's not allowed to have more than 4 levels depth: "
                      "%s") % one.name)
            for num in range(1, 5):
                if num > len(parts):
                    # Empty subfield in this case
                    one[one.field_n(num, True)] = False
                    continue
                field_name = parts[num - 1]
                model = one.model_n(num)
                # You could get to failing constraint while populating the
                # fields, so we skip the uniqueness check and manually check
                # the full constraint after the loop
                one.with_context(skip_check=True)[one.field_n(num, True)] = (
                    one._get_field_id(model, field_name))
            one._check_name()

    @api.multi
    @api.constrains("field1_id", "field2_id", "field3_id", "field4_id")
    def _check_name(self):
        for one in self:
            if not one.label:
                raise exceptions.ValidationError(
                    _("Field '%s' does not exist") % one.name)
            if not one.env.context.get('skip_check'):
                lines = one.search([('export_id', '=', one.export_id.id),
                                    ('name', '=', one.name)])
                if len(lines) > 1:
                    raise exceptions.ValidationError(
                        _("Field '%s' already exists") % one.name)

    @api.multi
    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self._inverse_name()
        else:
            self.field1_id = False
            self.field2_id = False
            self.field3_id = False
            self.field4_id = False

    @api.model
    def _get_field_id(self, model, name):
        """Get a field object from its model and name.

        :param int model:
            ``ir.model`` object that contains the field.

        :param str name:
            Technical name of the field, like ``child_ids``.
        """
        field = self.env["ir.model.fields"].search(
            [("name", "=", name),
             ("model_id", "=", model.id)])
        if not field.exists():
            raise exceptions.ValidationError(
                _("Field '%s' not found in model '%s'") % (name, model.model))
        return field

    @api.multi
    def field_n(self, n, only_name=False):
        """Helper to choose the field according to its indentation level.

        :param int n:
            Number of the indentation level to choose the field, from 1 to 3.

        :param bool only_name:
            Return only the field name, or return its value.
        """
        name = "field%d_id" % n
        return name if only_name else self[name]

    @api.multi
    def model_n(self, n, only_name=False):
        """Helper to choose the model according to its indentation level.

        :param int n:
            Number of the indentation level to choose the model, from 1 to 3.

        :param bool only_name:
            Return only the model name, or return its value.
        """
        name = "model%d_id" % n
        return name if only_name else self[name]
