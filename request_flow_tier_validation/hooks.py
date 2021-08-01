# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api

ACTIONS = ("request_flow.request_request_action_to_review",)


def uninstall_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for action_id in ACTIONS:
            action = env.ref(action_id)
            action.write(
                {
                    "context": "{}",
                    "domain": "[('approver_id','=',uid)," "('state','=','pending')]",
                }
            )
