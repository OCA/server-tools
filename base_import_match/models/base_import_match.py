# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0-or-later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class BaseImportMatch(models.Model):
    """Match configuration for record import.

    Defines which fields to use as lookup keys when importing records,
    instead of relying on External IDs that differ across databases.

    Multiple fields can be combined: all of them must match simultaneously
    (AND condition). Configurations are evaluated in *sequence* order; the
    first one that finds a unique record wins.

    Example — update e-commerce category descriptions by name + seo_name:
        Model  : product.public.category
        Fields : name, seo_name
    """

    _name = "base_import.match"
    _description = "Import Match Configuration"
    _order = "sequence, id"
    _rec_name = "name"

    name = fields.Char(
        required=True,
        translate=True,
        help="Human-readable label for this match configuration.",
    )
    sequence = fields.Integer(
        string="Priority",
        default=10,
        help=(
            "Evaluation order when several configurations exist for the same "
            "model. The first one that returns a unique record is applied."
        ),
    )
    active = fields.Boolean(
        default=True,
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
        domain=[("transient", "=", False)],
        help="Odoo model to which this configuration applies.",
    )
    model_name = fields.Char(
        related="model_id.model",
        store=True,
        index=True,
        string="Technical Model Name",
    )
    field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        relation="base_import_match_field_rel",
        column1="match_id",
        column2="field_id",
        string="Match Fields",
        domain=(
            "[('model_id', '=', model_id),"
            " ('ttype', 'not in',"
            "  ['one2many', 'many2many', 'binary', 'html']),"
            " ('store', '=', True)]"
        ),
        help=(
            "Fields used to look up existing records. All selected fields "
            "must match simultaneously (AND). For many2one fields the "
            "related record is resolved by display name."
        ),
    )

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------

    @api.constrains("field_ids")
    def _check_field_ids(self):
        for record in self:
            if not record.field_ids:
                raise ValidationError(
                    _(
                        "At least one match field must be selected "
                        "in configuration '%(name)s'.",
                        name=record.name,
                    )
                )

    # ------------------------------------------------------------------
    # Onchange helpers
    # ------------------------------------------------------------------

    @api.onchange("model_id")
    def _onchange_model_id(self):
        """Clear field selection when the model changes."""
        self.field_ids = [Command.clear()]
