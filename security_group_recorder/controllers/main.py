# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import http

from odoo.addons.web.controllers.main import Action, request

from ..models.ir_model import _check_action_profiled_user


class ActionExtended(Action):
    @http.route()
    def load(self, action_id, additional_context=None):
        action = super().load(
            action_id=action_id, additional_context=additional_context
        )
        if isinstance(action, dict):
            env = request.env
            action_id = action.get("id")
            action_type = action.get("type")
            model = action.get("res_model") or ""
            name = env[action_type].sudo().browse(action_id).xml_id
            _check_action_profiled_user(
                env, request._uid, name, action, model, action_type
            )
        return action
