# -*- coding: utf-8 -*-
from openerp import api, models


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    @api.model
    def action_base_config_settings(self):
        res = self.create({'auth_signup_uninvited': True})
        res.execute()
        return True
