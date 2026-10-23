# Copyright 2026 Mayur Bechara <becharamayur49@gmail.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class AIChatGPTModel(models.Model):
    _name = "ai.chatgpt.model"
    _description = "ChatGPT Subscription Supported Model"
    _order = "sequence, id"

    name = fields.Char(
        string="Model Display Name",
        required=True,
        help="User-friendly name displayed in AI Agent dropdown (e.g., 'GPT-5.6 Luna').",
    )
    code = fields.Char(
        string="Technical Model ID",
        required=True,
        index=True,
        help="Technical model slug sent to OpenAI Codex endpoint (e.g., 'gpt-5.6-luna').",
    )
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to hide this model from AI Agent selection when deprecated by OpenAI.",
    )
    description = fields.Text(
        string="Notes",
        help="Optional notes regarding model capabilities, tiers, or context window.",
    )

    _code_unique = models.Constraint("UNIQUE (code)", "The technical model ID must be unique!")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self._refresh_provider_cache()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._refresh_provider_cache()
        return res

    def unlink(self):
        res = super().unlink()
        self._refresh_provider_cache()
        return res

    @api.model
    def _refresh_provider_cache(self):
        """Update Odoo's in-memory LLM providers registry when models change."""
        from odoo.addons.ai.utils import llm_providers
        active_models = self.search([("active", "=", True)], order="sequence, id")
        for p_idx, provider in enumerate(llm_providers.PROVIDERS):
            if provider.name == "openai":
                existing_keys = {m[0] for m in provider.llms}
                new_llms = list(provider.llms)
                for m in active_models:
                    if m.code not in existing_keys:
                        new_llms.append((m.code, m.name))
                        existing_keys.add(m.code)
                llm_providers.PROVIDERS[p_idx] = provider._replace(llms=new_llms)
