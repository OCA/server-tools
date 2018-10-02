# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _, SUPERUSER_ID
from openerp.exceptions import UserError
from openerp.addons.server_environment import serv_config


SECTION = 'ir.config_parameter'


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
                self.set_param(cr, SUPERUSER_ID, key, cvalue)
                value = cvalue
        if value is None:
            return default
        return value

    @api.model
    def create(self, vals):
        key = vals.get('key')
        if serv_config.has_option(SECTION, key):
            # enforce value from config file
            vals = dict(vals, value=serv_config.get(SECTION, key))
        return super(IrConfigParameter, self).create(vals)

    @api.multi
    def write(self, vals):
        for rec in self:
            key = vals.get('key') or rec.key
            if serv_config.has_option(SECTION, key):
                # enforce value from config file
                newvals = dict(vals, value=serv_config.get(SECTION, key))
            else:
                newvals = vals
            super(IrConfigParameter, rec).write(newvals)
