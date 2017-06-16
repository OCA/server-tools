# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os

from odoo import _, api, models
from odoo.exceptions import AccessError

from .res_groups import THRESHOLD_MANAGER

MAX_DB_USER_PARAM = 'user.threshold.database'
THRESHOLD_HIDE = str(os.environ.get('USER_THRESHOLD_HIDE', '')) == '1'


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.multi
    def unlink(self):
        """
        Override to disallow deletion of the user threshold parameter
        when the user does not have the right access
        """
        for rec in self.filtered(lambda r: r.key == MAX_DB_USER_PARAM):
            if not self.env.user.has_group(THRESHOLD_MANAGER):
                raise AccessError(_(
                    'You must be a member of the `User Threshold Manager` '
                    'to delete this parameter'
                ))
        return super(IrConfigParameter, self).unlink()

    @api.multi
    def write(self, vals):
        """
        Override to disallow manipulation of the user threshold parameter
        when the user does not have the right access
        """
        for rec in self.filtered(lambda r: r.key == MAX_DB_USER_PARAM):
            if not self.env.user.has_group(THRESHOLD_MANAGER):
                raise AccessError(_(
                    'You must be a member of the `User Threshold Manager` '
                    'to set this parameter'
                ))
        return super(IrConfigParameter, self).write(vals)
