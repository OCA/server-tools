# Copyright 2024 jesanmor - Jesús Sánchez <jesanmor.dev@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def uninstall_hook(env):
    records = env["server.action.input.box"].search([])
    actions = records.mapped("ir_action_server_id")
    records.write({"ir_action_server_id": False})
    actions.unlink()
