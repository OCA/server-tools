# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

# Business actions shipped with a known, complete inverse. They live in Python
# rather than in a data file because the models they target belong to modules
# that may well be installed after this one. A model whose module is missing is
# simply skipped when the hooks are registered.
DEFAULT_ACTIONS = {
    "sale.order": {"action_confirm": ("_action_cancel", "action_draft")},
    "purchase.order": {"button_confirm": ("button_cancel", "button_draft")},
    "account.move": {"action_post": ("button_draft",)},
}


class GlobalUndoAction(models.Model):
    """A business method whose effect can be reverted by calling other methods.

    Only configured actions are journalled as a single undoable step: undoing a
    business action means trusting the inverse to leave the records consistent,
    which is a judgement call belonging to whoever configures the database.
    """

    _name = "global.undo.action"
    _inherit = "global.undo.config.mixin"
    _description = "Global Undo Business Action"
    _order = "model_id, method"

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
    method = fields.Char(
        required=True,
        help="Method to make undoable, for example action_confirm.",
    )
    undo_methods = fields.Char(
        required=True,
        help="Comma separated methods that, called in order, revert the "
        "action. For example: _action_cancel, action_draft",
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "method_unique",
            "unique(model_id, method)",
            "This action is already configured.",
        ),
    ]

    # Constraints and onchanges

    @api.constrains("method", "undo_methods")
    def _check_methods(self):
        for rule in self:
            model = self.env.get(rule.model_name)
            if model is None:
                continue
            for name in [rule.method] + rule._gu_undo_methods():
                if not hasattr(model, name):
                    raise ValidationError(
                        _(
                            "%(model)s has no method %(method)s.",
                            model=rule.model_name,
                            method=name,
                        )
                    )

    # Business methods

    def _gu_undo_methods(self):
        self.ensure_one()
        return [
            name.strip()
            for name in (self.undo_methods or "").split(",")
            if name.strip()
        ]

    @api.model
    def _gu_registered(self):
        """Return ``{model_name: {method: (undo_method, ...)}}`` for the hook.

        Starts from :data:`DEFAULT_ACTIONS` and lets the configured rules add
        new actions, change an inverse, or archive a default one away.
        """
        registered = {
            model: dict(methods) for model, methods in DEFAULT_ACTIONS.items()
        }
        # The table does not exist yet the very first time the registry is
        # loaded during this module's own installation.
        if not tools.sql.table_exists(self.env.cr, self._table):
            return registered
        for rule in self.sudo().with_context(active_test=False).search([]):
            methods = registered.setdefault(rule.model_name, {})
            if rule.active:
                methods[rule.method] = tuple(rule._gu_undo_methods())
            else:
                methods.pop(rule.method, None)
        return registered

    def _gu_config_changed(self):
        """Patching and unpatching methods only takes effect on a reload."""
        self.env.registry.registry_invalidated = True
