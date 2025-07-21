from odoo import http
from odoo.http import request


class VapiIntegrationController(http.Controller):


    @http.route('/polpo_vapi_integration/widget_config', type='json', auth='user')
    def widget_config(self):
        user = request.env.user

        api_key = request.env['ir.config_parameter'].sudo().get_param('vapi_api_key')
        assistant_id = request.env['ir.config_parameter'].sudo().get_param('vapi_assistant_id')

        return {
            "api_key": api_key,
            "assistant_id": assistant_id,
            "userId": user.id,
            "userName": user.name
        }
