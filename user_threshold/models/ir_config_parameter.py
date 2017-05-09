# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os

from odoo import _, api, models
from odoo.exceptions import AccessError

MAX_DB_USER_PARAM = 'user.threshold.database'
HIDE_THRESHOLD = str(os.environ.get('USER_THRESHOLD_HIDE', '')) == '1'


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    def _can_manipulate_th(self):
        """ Check to see if the user is a member of the correct group
         Returns:
             True when the user is a member of the threshold manager group
        """
        return self.env.user.has_group(
            'user_threshold.group_threshold_manager'
        )

    @api.multi
    def unlink(self):
        """ Override to disallow deletion of the user threshold parameter
        when the user does not have the right access
        """
        for rec in self.filtered(lambda r: r.key == MAX_DB_USER_PARAM):
            if not self._can_manipulate_th():
                raise AccessError(_(
                    'You do not have access to delete this parameter'
                ))
        return super(IrConfigParameter, self).unlink()

    @api.multi
    def write(self, vals):
        """ Override to disallow manipulation of the user threshold parameter
        when the user does not have the right access
        """
        for rec in self.filtered(lambda r: r.key == MAX_DB_USER_PARAM):
            if not self._can_manipulate_th():
                raise AccessError(_(
                    'You do not have access to set this parameter'
                ))
        return super(IrConfigParameter, self).write(vals)
