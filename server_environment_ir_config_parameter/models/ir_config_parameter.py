# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _, SUPERUSER_ID
from openerp.exceptions import UserError
from openerp.addons.server_environment import serv_config


SECTION = 'ir.config_parameter'
CTX_NO_CHECK = 'icp_no_check'


class IrConfigParameter(models.Model):

    _inherit = 'ir.config_parameter'

    def get_param(self, cr, uid, key, default=False, context=None):
        value = super(IrConfigParameter, self).get_param(
            cr, uid, key, default=None, context=context)
        if serv_config.has_option(SECTION, key):
            cvalue = serv_config.get(SECTION, key)
            if not cvalue:
                raise UserError(_("Key %s is empty in "
                                  "server_environment_file") %
                                (key, ))
            if cvalue != value:
                # we write in db on first access;
                # should we have preloaded values in database at,
                # server startup, modules loading their parameters
                # from data files would break on unique key error.
                self.set_param(
                    cr, SUPERUSER_ID, key, cvalue,
                    context={CTX_NO_CHECK: True})
                value = cvalue
        if value is None:
            return default
        return value

    def _check_not_in_config(self, keys):
        if self.env.context.get(CTX_NO_CHECK):
            return
        if not serv_config.has_section(SECTION):
            return
        config_icp_keys = set(serv_config.options(SECTION)) & set(keys)
        if config_icp_keys:
            raise UserError(_("System Parameter(s) %s is/are defined "
                              "in server_environment_files.") %
                            (config_icp_keys, ))

    @api.model
    def create(self, vals):
        self._check_not_in_config([vals.get('key')])
        return super(IrConfigParameter, self).create(vals)

    @api.multi
    def write(self, vals):
        self._check_not_in_config(self.mapped('key'))
        return super(IrConfigParameter, self).write(vals)

    @api.multi
    def unlink(self):
        self._check_not_in_config(self.mapped('key'))
        return super(IrConfigParameter, self).unlink()
