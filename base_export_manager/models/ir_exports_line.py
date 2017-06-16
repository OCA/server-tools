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
    sequence = fields.Integer()
    label = fields.Char(
        compute="_compute_label")

    @api.model
    def _default_model1_id(self):
        """Default model depending on context."""
        return self.env.context.get("default_model1_id", False)

    @api.multi
    @api.depends("field1_id", "field2_id", "field3_id")
    def _compute_name(self):
        """Get the name from the selected fields."""
        for s in self:
            s.name = "/".join((s.field_n(num).name
                               for num in range(1, 4)
                               if s.field_n(num)))

    @api.multi
    @api.depends("field1_id")
    def _compute_model2_id(self):
        """Get the related model for the second field."""
        ir_model = self.env["ir.model"]
        for s in self:
            s.model2_id = (
                s.field1_id.ttype and
                "2" in s.field1_id.ttype and
                ir_model.search([("model", "=", s.field1_id.relation)]))

    @api.multi
    @api.depends("field2_id")
    def _compute_model3_id(self):
        """Get the related model for the third field."""
        ir_model = self.env["ir.model"]
        for s in self:
            s.model3_id = (
                s.field2_id.ttype and
                "2" in s.field2_id.ttype and
                ir_model.search([("model", "=", s.field2_id.relation)]))

    @api.multi
    @api.depends('name')
    def _compute_label(self):
        """Column label in a user-friendly format and language."""
        translations = self.env["ir.translation"]
        for s in self:
            parts = list()
            for num in range(1, 4):
                field = s.field_n(num)
                if not field:
                    break

                # Translate label if possible
                parts.append(
                    translations.search([
                        ("type", "=", "field"),
                        ("lang", "=", self.env.context.get("lang")),
                        ("name", "=", "%s,%s" % (s.model_n(num).model,
                                                 field.name)),
                    ]).value or
                    field.display_name)
            s.label = ("%s (%s)" % ("/".join(parts), s.name)
                       if parts and s.name else False)

    @api.multi
    def _inverse_name(self):
        """Get the fields from the name."""
        for s in self:
            # Field names can have up to only 3 indentation levels
            parts = s.name.split("/", 2)

            for num in range(1, 4):
                try:
                    # Fail in excessive subfield level
                    field_name = parts[num - 1]
                except IndexError:
                    # Remove subfield on failure
                    s[s.field_n(num, True)] = False
                else:
                    model = s.model_n(num)
                    s[s.field_n(num, True)] = self._get_field_id(
                        model, field_name)

    @api.multi
    @api.constrains("field1_id", "field2_id", "field3_id")
    def _check_name(self):
        for rec_id in self:
            if not rec_id.label:
                raise exceptions.ValidationError(
                    _("Field '%s' does not exist") % rec_id.name)
            lines = self.search([('export_id', '=', rec_id.export_id.id),
                                 ('name', '=', rec_id.name)])
            if len(lines) > 1:
                raise exceptions.ValidationError(
                    _("Field '%s' already exists") % rec_id.name)

    @api.model
    def _install_base_export_manager(self):
        """Populate ``field*_id`` fields."""
        self.search([("export_id", "=", False)]).unlink()
        self.search([("field1_id", "=", False),
                     ("name", "!=", False)])._inverse_name()

    @api.model
    def _get_field_id(self, model, name):
        """Get a field object from its model and name.

        :param int model:
            ``ir.model`` object that contains the field.

        :param str name:
            Technical name of the field, like ``child_ids``.
        """
        return self.env["ir.model.fields"].search(
            [("name", "=", name),
             ("model_id", "=", model.id)])

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
