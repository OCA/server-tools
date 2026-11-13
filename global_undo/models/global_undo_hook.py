# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models

from .base import gu_suspend


class GlobalUndoHook(models.AbstractModel):
    """Wraps the business actions configured in ``global.undo.action``.

    A dedicated abstract model is used because ``_register_hook`` runs once per
    model in the registry; putting it on ``base`` would run it hundreds of
    times. Odoo core is not modified: the methods are wrapped in place, exactly
    as ``base_automation`` does, and the original is kept on ``origin``.
    """

    _name = "global.undo.hook"
    _description = "Global Undo Business Action Hook"

    def _register_hook(self):
        def make_action(method_name, undo_methods):
            def action(self, *args, **kwargs):
                if not self._gu_is_tracked():
                    return action.origin(self, *args, **kwargs)
                # The action is the undoable unit; its writes are not.
                with gu_suspend(self.env):
                    result = action.origin(self, *args, **kwargs)
                # Labelled afterwards: actions such as posting assign the name.
                targets = [
                    (record.id, record._gu_display_name(), record._gu_write_stamp())
                    for record in self.exists()
                ]
                self.env["global.undo.transaction"]._gu_log_action(
                    self._name, method_name, undo_methods, targets
                )
                return result

            action._gu_patched = True
            return action

        registered = self.env["global.undo.action"]._gu_registered()
        for model_name, methods in registered.items():
            if model_name not in self.env:
                continue
            model_class = self.env.registry[model_name]
            for method_name, undo_methods in methods.items():
                origin = getattr(model_class, method_name, None)
                if origin is None or getattr(origin, "_gu_patched", False):
                    continue
                if not all(hasattr(model_class, name) for name in undo_methods):
                    continue
                patched = make_action(method_name, undo_methods)
                patched.origin = origin
                setattr(model_class, method_name, patched)
