# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE - Cédric Pigeon
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, tools

DELAY_KEY = 'inactive_session_time_out_delay'
IGNORED_PATH_KEY = 'inactive_session_time_out_ignored_url'


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    @tools.ormcache(skiparg=0)
    def get_session_parameters(self, db):
        Parameters = self.env['ir.config_parameter']
        delay = Parameters.get_param(DELAY_KEY, 7200)
        delay = (int(delay) if delay else False)
        urls = Parameters.get_param(IGNORED_PATH_KEY, '')
        urls = (urls.split(',') if urls else [])
        return delay, urls

    @api.multi
    def write(self, vals, context=None):
        res = super(IrConfigParameter, self).write(vals)
        if self.key in [DELAY_KEY, IGNORED_PATH_KEY]:
            self.get_session_parameters.clear_cache(self)
        return res
