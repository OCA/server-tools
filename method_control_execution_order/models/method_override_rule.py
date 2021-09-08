# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from itertools import groupby

from odoo import fields, models

_logger = logging.getLogger(__name__)


class MethodOverrideRule(models.Model):
    _name = "method.override.rule"
    _description = "Representation of a method override"

    method_name = fields.Char(string="Name", help="The name of the overrideed method",)
    method_model = fields.Char(string="Model", help="The name of the overridden model",)
    method_delegate_name = fields.Char(
        help=(
            "The name of the method that will be used to "
            "alter the output of the overrideed method."
        )
    )
    sequence = fields.Integer()

    _sql_constraints = [
        (
            "unique_delegate_method_per_method",
            "unique(method_name, method_model, method_delegate_name)",
            "There can be only one delegate method for an overridden method.",
        ),
    ]

    def _register_hook(self):
        self._patch_methods()

    def _make_patched_method(self):
        rule_ids = self.ids

        def patched_method(self, *args, **kwargs):
            res = patched_method.origin(self, *args, **kwargs)
            rules = self.env["method.override.rule"].browse(rule_ids).sorted("sequence")
            for rule in rules:
                delegate_method = getattr(self, rule.method_delegate_name, None)
                if not delegate_method:
                    _logger.error(
                        f"No method named {rule.method_delegate_name} "
                        f"for {rule.method_model}"
                    )
                    continue
                res = delegate_method(res)
            return res

        return patched_method

    def _patch_methods(self):
        groups = self._get_groupped_rules()
        for (model_name, method_name), rules in groups:
            rule_ids = [rule.id for rule in rules]
            rules = self.browse(rule_ids)
            model = self.env[model_name]
            patched_method = rules._make_patched_method()
            model._patch_method(method_name, patched_method)

    def _get_groupped_rules(self):
        overrides = self.search([], order="method_model, method_name")
        return groupby(overrides, key=lambda o: (o.method_model, o.method_name))
