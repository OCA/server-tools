# -*- coding: utf-8 -*-
# Copyright 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)


class BaseImportMatch(models.Model):
    _name = "base_import.match"
    _description = "Deduplicate settings prior to CSV imports."
    _order = "sequence, name"

    name = fields.Char(
        compute="_compute_name",
        store=True,
        index=True)
    sequence = fields.Integer(index=True)
    model_id = fields.Many2one(
        "ir.model",
        "Model",
        required=True,
        ondelete="cascade",
        domain=[("transient", "=", False)],
        help="In this model you will apply the match.")
    model_name = fields.Char(
        related="model_id.model",
        store=True,
        index=True)
    field_ids = fields.One2many(
        comodel_name="base_import.match.field",
        inverse_name="match_id",
        string="Fields",
        required=True,
        help="Fields that will define an unique key.")

    @api.onchange("model_id")
    def _onchange_model_id(self):
        self.field_ids = False

    @api.depends("model_id", "field_ids")
    def _compute_name(self):
        """Automatic self-descriptive name for the setting records."""
        for one in self:
            one.name = u"{}: {}".format(
                one.model_id.display_name,
                " + ".join(one.field_ids.mapped("display_name")),
            )

    @api.model
    def _match_find(self, model, converted_row, imported_row):
        """Find a update target for the given row.

        This will traverse by order all match rules that can be used with the
        imported data, and return a match for the first rule that returns a
        single result.

        :param odoo.models.Model model:
            Model object that is being imported.

        :param dict converted_row:
            Row converted to Odoo api format, like the 3rd value that
            :meth:`odoo.models.Model._convert_records` returns.

        :param dict imported_row:
            Row as it is being imported, in format::

                {
                    "field_name": "string value",
                    "other_field": "True",
                    ...
                }

        :return odoo.models.Model:
            Return a dataset with one single match if it was found, or an
            empty dataset if none or multiple matches were found.
        """
        # Get usable rules to perform matches
        usable = self._usable_rules(model._name, converted_row)
        # Traverse usable combinations
        for combination in usable:
            combination_valid = True
            domain = list()
            for field in combination.field_ids:
                # Check imported value if it is a conditional field
                if field.conditional:
                    # Invalid combinations are skipped
                    if imported_row[field.name] != field.imported_value:
                        combination_valid = False
                        break
                domain.append((field.name, "=", converted_row[field.name]))
            if not combination_valid:
                continue
            match = model.search(domain)
            # When a single match is found, stop searching
            if len(match) == 1:
                return match
            elif match:
                _logger.warning(
                    "Found multiple matches for model %s and domain %s; "
                    "falling back to default behavior (create new record)",
                    model._name,
                    domain,
                )
        # Return an empty match if none or multiple was found
        return model

    @api.model
    @tools.ormcache("model_name", "fields")
    def _usable_rules(self, model_name, fields):
        """Return a set of elements usable for calling ``load()``.

        :param str model_name:
            Technical name of the model where you are loading data.
            E.g. ``res.partner``.

        :param list(str|bool) fields:
            List of field names being imported.

        :return bool:
            Indicates if we should patch its load method.
        """
        result = self
        available = self.search([("model_name", "=", model_name)])
        # Use only criteria with all required fields to match
        for record in available:
            if all(f.name in fields for f in record.field_ids):
                result |= record
        return result


class BaseImportMatchField(models.Model):
    _name = "base_import.match.field"
    _description = "Field import match definition"

    name = fields.Char(
        related="field_id.name")
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Field",
        required=True,
        ondelete="cascade",
        domain="[('model_id', '=', model_id)]",
        help="Field that will be part of an unique key.")
    match_id = fields.Many2one(
        comodel_name="base_import.match",
        string="Match",
        ondelete="cascade",
        required=True)
    model_id = fields.Many2one(
        related="match_id.model_id")
    conditional = fields.Boolean(
        help="Enable if you want to use this field only in some conditions.")
    imported_value = fields.Char(
        help="If the imported value is not this, the whole matching rule will "
             "be discarded. Be careful, this data is always treated as a "
             "string, and comparison is case-sensitive so if you set 'True', "
             "it will NOT match '1' nor 'true', only EXACTLY 'True'.")

    @api.depends("conditional", "field_id", "imported_value")
    def _compute_display_name(self):
        for one in self:
            pattern = u"{name} ({cond})" if one.conditional else u"{name}"
            one.display_name = pattern.format(
                name=one.field_id.name,
                cond=one.imported_value,
            )

    @api.onchange("field_id", "match_id", "conditional", "imported_value")
    def _onchange_match_id_name(self):
        """Update match name."""
        self.mapped("match_id")._compute_name()
