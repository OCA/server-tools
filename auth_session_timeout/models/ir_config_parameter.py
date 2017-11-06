# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, tools


DELAY_KEY = 'inactive_session_time_out_delay'
IGNORED_PATH_KEY = 'inactive_session_time_out_ignored_url'


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @tools.ormcache(skiparg=0)
    def get_session_parameters(self, db, uid):
        cr = self.pool.cursor()
        ICP = api.Environment(cr, uid, {})['ir.config_parameter']
        delay = False
        urls = []
        try:
            delay = int(ICP.get_param(DELAY_KEY, 7200))
            urls = ICP.get_param(IGNORED_PATH_KEY, '').split(',')
        finally:
            cr.close()
        return delay, urls

    @api.multi
    def write(self, vals, context=None):
        res = super(IrConfigParameter, self).write(vals)
        if self.key in [DELAY_KEY, IGNORED_PATH_KEY]:
            self.get_session_parameters.clear_cache(self)
        return res
