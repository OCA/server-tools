# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, tools


class GlobalUndoExclusion(models.Model):
    """A model that must never be recorded, on top of the built-in blacklist."""

    _name = "global.undo.exclusion"
    _inherit = "global.undo.config.mixin"
    _description = "Global Undo Excluded Model"
    _order = "model_id"

    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
    )
    model_name = fields.Char(
        related="model_id.model",
        store=True,
        string="Technical Name",
    )
    reason = fields.Char(help="Why this model must not be undoable.")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("model_unique", "unique(model_id)", "This model is already excluded."),
    ]

    # Business methods

    @api.model
    @tools.ormcache()
    def _gu_excluded_models(self):
        """Technical names of the excluded models, cached for the CRUD hooks.

        This runs on every tracked write, so it must not hit the database each
        time; the cache is cleared whenever the configuration changes.
        """
        return frozenset(self.sudo().search([]).mapped("model_name"))

    def _gu_config_changed(self):
        self.env.registry.clear_cache()
