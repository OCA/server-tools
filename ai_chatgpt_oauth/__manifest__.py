# Copyright 2026 Mayur Bechara <becharamayur49@gmail.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "AI ChatGPT OAuth",
    "summary": "Use ChatGPT subscription authentication for Odoo AI chat with OpenAI API fallback for supporting services",
    "version": "19.0.1.0.0",
    "category": "Productivity/Artificial Intelligence",
    "author": "Mayur Bechara, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "LGPL-3",
    "maintainers": ["becharamayur"],
    "depends": ["base", "ai"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/ai_chatgpt_model_data.xml",
        "views/ai_chatgpt_model_views.xml",
        "wizard/chatgpt_oauth_wizard_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
