# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import AccessError

THRESHOLD_MANAGER = 'user_threshold.group_threshold_manager'


class ResGroups(models.Model):
    _inherit = 'res.groups'

    @api.multi
    def write(self, vals):
        """ Override write to verify that membership of the Threshold Manager
        group is not able to be set by users outside that group
        """
        manager = self.env.ref(THRESHOLD_MANAGER, raise_if_not_found=False)
        is_manager = self.env.user.has_group(THRESHOLD_MANAGER)
        if len(self.filtered(lambda r: r == manager)) and not is_manager:
            raise AccessError(_(
                'You must be a member of the `User Threshold Manager` group '
                'to grant access to it'
            ))
        return super(ResGroups, self).write(vals)
