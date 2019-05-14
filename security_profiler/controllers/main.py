# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import http
from ..models.ir_model import _check_action_profiled_user
from odoo.addons.web.controllers.main import request, Action, DataSet


class ActionExtended(Action):

    @http.route()
    def load(self, action_id, additional_context=None):
        action = super(ActionExtended, self).load(
            action_id=action_id, additional_context=additional_context)
        if isinstance(action, dict):
            env = request.env
            action_id = action.get('id')
            action_type = action.get('type')
            name = request.env[action_type].sudo().browse(action_id).xml_id
            _check_action_profiled_user(
                env, request._uid, name, action, action_type)
        return action


class DataSetExtended(DataSet):

    @http.route()
    def call_button(self, model, method, args,
                    domain_id=None, context_id=None):
        action = super(DataSetExtended, self).call_button(
            model=model, method=method, args=args,
            domain_id=domain_id, context_id=context_id)
        if isinstance(action, dict):
            env = request.env
            _check_action_profiled_user(env, request._uid, method, action)
        return action
