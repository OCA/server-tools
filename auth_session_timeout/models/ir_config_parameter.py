# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, tools

DELAY_KEY = 'inactive_session_time_out_delay'
IGNORED_PATH_KEY = 'inactive_session_time_out_ignored_url'


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    def get_session_parameters(self, db):
        """Method no longer required by module auth_session_timeout.
        Left here in case any other modules referenced it.
        """
        delay = False
        urls = []
        with openerp.registry(db).cursor() as cr:
            uid, context = self.env.uid, self.env.context
            with api.Envionment.manage():
                env = api.Envionment(cr, uid, context)
                delay = self.with_env(env)._auth_timeout_get_parameter_delay()
                urls = self.with_env(env)._auth_timeout_get_parameter_urls()
        return delay, urls

    @tools.ormcache()
    def _auth_timeout_get_parameter_delay(self):
        param_model = self.env['ir.config_parameter']
        delay = int(param_model.sudo().get_param(DELAY_KEY, 7200))
        return delay

    @tools.ormcache()
    def _auth_timeout_get_parameter_ignoredurls(self):
        param_model = self.env['ir.config_parameter']
        urls = param_model.sudo().get_param(IGNORED_PATH_KEY, '').split(',')
        return urls

    @api.multi
    def write(self, vals, context=None):
        res = super(IrConfigParameter, self).write(vals)
        if self.key == DELAY_KEY:
            self._auth_timeout_get_parameter_delay.clear_cache(self)
            self.get_session_parameters.clear_cache(self)
        elif self.key == IGNORED_PATH_KEY:
            self._auth_timeout_get_parameter_ignoredurls.clear_cache(self)
            self.get_session_parameters.clear_cache(self)
        return res
