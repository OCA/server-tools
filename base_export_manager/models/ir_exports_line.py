# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería S.L. - Antonio Espinosa
# Copyright 2015-2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, exceptions
from openerp.tools.translate import _


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

    @api.one
    @api.depends("field1_id", "field2_id", "field3_id", "field4_id")
    def _compute_name(self):
        """Get the name from the selected fields."""
        name = "/".join((self.field_n(num).name for num in range(1, 5)
                         if self.field_n(num)))
        if name != self.name:
            self.name = name

    @api.one
    @api.depends("field1_id")
    def _compute_model2_id(self):
        """Get the related model for the second field."""
        ir_model = self.env["ir.model"]
        self.model2_id = (
            self.field1_id.ttype and
            "2" in self.field1_id.ttype and
            ir_model.search([("model", "=", self.field1_id.relation)]))

    @api.one
    @api.depends("field2_id")
    def _compute_model3_id(self):
        """Get the related model for the third field."""
        ir_model = self.env["ir.model"]
        self.model3_id = (
            self.field2_id.ttype and
            "2" in self.field2_id.ttype and
            ir_model.search([("model", "=", self.field2_id.relation)]))

    @api.one
    @api.depends("field3_id")
    def _compute_model4_id(self):
        """Get the related model for the third field."""
        ir_model = self.env["ir.model"]
        self.model4_id = (
            self.field3_id.ttype and
            "2" in self.field3_id.ttype and
            ir_model.search([("model", "=", self.field3_id.relation)]))

    @api.one
    @api.depends('name')
    def _compute_label(self):
        """Column label in a user-friendly format and language."""
        try:
            parts = list()
            for num in range(1, 5):
                field = self.field_n(num)
                if not field:
                    break
                # Translate label if possible
                parts.append(
                    self.env[self.model_n(num).model]._fields[field.name]
                    .get_description(self.env)["string"])
            self.label = ("%s (%s)" % ("/".join(parts), self.name)
                          if parts and self.name else False)
        except KeyError:
            pass

    @api.one
    def _inverse_name(self):
        """Get the fields from the name."""
        # Field names can have up to only 3 indentation levels
        parts = self.name.split("/")
        if len(parts) > 4:
            raise exceptions.ValidationError(
                _("It's not allowed to have more than 4 levels depth: "
                  "%s") % self.name)
        for num in range(1, 5):
            if num > len(parts):
                # Empty subfield in this case
                self[self.field_n(num, True)] = False
                continue
            field_name = parts[num - 1]
            model = self.model_n(num)
            self.with_context(skip_check=True)[self.field_n(num, True)] = (
                self._get_field_id(model, field_name))
        self._check_name()

    @api.one
    @api.constrains("field1_id", "field2_id", "field3_id", "field4_id")
    def _check_name(self):
        if not self.label:
            raise exceptions.ValidationError(
                _("Field '%s' does not exist") % self.name)
        if not self.env.context.get('skip_check'):
            lines = self.search([('export_id', '=', self.export_id.id),
                                 ('name', '=', self.name)])
            if len(lines) > 1:
                raise exceptions.ValidationError(
                    _("Field '%s' already exists") % self.name)

    @api.onchange('name')
    def onchange_name(self):
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
