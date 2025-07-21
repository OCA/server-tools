from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vapi_api_key = fields.Char(string="Vapi API Key",
                               config_parameter='vapi_api_key')
    vapi_assistant_id = fields.Char(string="Vapi Assistant ID",
                                    config_parameter='vapi_assistant_id')
