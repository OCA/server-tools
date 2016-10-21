# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, tools


DELAY_KEY = 'inactive_session_time_out_delay'
IGNORED_PATH_KEY = 'inactive_session_time_out_ignored_url'


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    @tools.ormcache('self.env.cr.dbname')
    def get_session_parameters(self):
        ConfigParam = self.env['ir.config_parameter']
        delay = ConfigParam.get_param(DELAY_KEY, 7200)
        urls = ConfigParam.get_param(IGNORED_PATH_KEY, '').split(',')
        return int(delay), urls

    @api.multi
    def write(self, vals):
        res = super(IrConfigParameter, self).write(vals)
        for rec_id in self:
            if rec_id.key in (DELAY_KEY, IGNORED_PATH_KEY):
                self.get_session_parameters.clear_cache(self)
        return res
