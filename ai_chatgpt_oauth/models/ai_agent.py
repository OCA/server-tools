# Copyright 2026 Mayur Bechara <becharamayur49@gmail.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, models

from .chatgpt_models import get_chatgpt_models


class AIAgent(models.Model):
    _inherit = "ai.agent"

    @api.model
    def _get_llm_model_selection(self):
        selection = super()._get_llm_model_selection()
        existing_keys = {item[0] for item in selection}

        available_chatgpt_models = get_chatgpt_models(self.env)
        for model_key, model_label in available_chatgpt_models:
            if model_key not in existing_keys:
                selection.append((model_key, model_label))

        return selection
