# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import functools

from odoo import api, fields, models, tools

AUTH_METHOD_CACHE_FIELDS = {"auth_method_ids", "model_id", "state"}


class AuditlogRule(models.Model):
    _inherit = "auditlog.rule"

    auth_method_ids = fields.Many2many(
        "auditlog.auth.method",
        "auditlog_rule_auth_method_rel",
        "rule_id",
        "auth_method_id",
        string="Authentication Methods",
        help="Only the operations done through the checked methods are logged. "
        "When none is checked, every method is logged.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        rules = super().create(vals_list)
        self.env.registry.clear_cache()
        return rules

    def write(self, vals):
        res = super().write(vals)
        if AUTH_METHOD_CACHE_FIELDS.intersection(vals):
            self.env.registry.clear_cache()
        return res

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_cache()
        return res

    @api.model
    @tools.ormcache("model_name")
    def _get_auth_method_codes(self, model_name):
        rule = self.search([("model_id.model", "=", model_name)], limit=1)
        return frozenset(rule.auth_method_ids.mapped("code")) or None

    @api.model
    def _auth_method_allows(self, model_name, code=None):
        codes = self._get_auth_method_codes(model_name)
        if codes is None:
            return True
        if code is None:
            code = self.env["auditlog.auth.method"]._get_current_auth_info()[0]
        return code in codes

    def _patch_method(self, model, method_name, check_attr):
        result = super()._patch_method(model, method_name, check_attr)
        if result:
            model_class = type(model)
            audited = getattr(model_class, method_name)
            setattr(model_class, method_name, self._make_auth_method_gate(audited))
        return result

    @api.model
    def _make_auth_method_gate(self, audited):
        original = audited.origin

        @functools.wraps(audited)
        def gate(records, *args, **kwargs):
            if records.env.context.get("auditlog_disabled") or records.env[
                "auditlog.rule"
            ].sudo()._auth_method_allows(records._name):
                return audited(records, *args, **kwargs)
            return original(records, *args, **kwargs)

        gate.origin = original
        return gate

    def create_logs(
        self,
        uid,
        res_model,
        res_ids,
        method,
        old_values=None,
        new_values=None,
        additional_log_values=None,
    ):
        auth_method = self.env["auditlog.auth.method"]
        code, mfa_method, api_key_name = auth_method._get_current_auth_info()
        if not self._auth_method_allows(res_model, code=code):
            return
        additional_log_values = dict(
            additional_log_values or {},
            auth_method_id=auth_method._get_id_by_code(code),
            auth_mfa_method=mfa_method,
            auth_api_key_name=api_key_name,
        )
        return super().create_logs(
            uid,
            res_model,
            res_ids,
            method,
            old_values=old_values,
            new_values=new_values,
            additional_log_values=additional_log_values,
        )
