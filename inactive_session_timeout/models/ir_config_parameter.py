# -*- coding: utf-8 -*-
##############################################################################

#     This file is part of inactive_session_timeout, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     inactive_session_timeout is free software: you can redistribute it
#     and/or modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     inactive_session_timeout is distributed in the hope that it will
#     be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with inactive_session_timeout.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, api

from openerp import tools
from openerp import SUPERUSER_ID

DELAY_KEY = 'inactive_session_time_out_delay'
IGNORED_PATH_KEY = 'inactive_session_time_out_ignored_url'


class ir_config_parameter(models.Model):
    _inherit = 'ir.config_parameter'

    @tools.ormcache(skiparg=0)
    def get_session_parameters(self, db):
        param_model = self.pool['ir.config_parameter']
        cr = self.pool.cursor()
        delay = False
        urls = []
        try:
            delay = int(param_model.get_param(
                cr, SUPERUSER_ID, DELAY_KEY, 7200))
            urls = param_model.get_param(
                cr, SUPERUSER_ID, IGNORED_PATH_KEY, '').split(',')
        finally:
            cr.close()
        return delay, urls

    @api.multi
    def write(self, vals, context=None):
        res = super(ir_config_parameter, self).write(vals)
        if self.key in [DELAY_KEY, IGNORED_PATH_KEY]:
            self.get_session_parameters.clear_cache(self)
        return res
