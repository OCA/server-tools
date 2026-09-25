# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    templates = env["xlsx.template"].search([("export_ids", "!=", False)])
    for template in templates:
        template.add_export_action()
