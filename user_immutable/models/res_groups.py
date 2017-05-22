# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import AccessError

IMMUTABLE = 'user_immutable.group_immutable'


class ResGroups(models.Model):

    _inherit = 'res.groups'

    @api.multi
    def write(self, vals):
        """ Override write to verify that access to the `Immutable` group is
        not given or removed by users without access
        """
        if not vals.get('users') or self.env.user.has_group(IMMUTABLE):
            return super(ResGroups, self).write(vals)
        immutable = self.env.ref(IMMUTABLE, raise_if_not_found=False)
        if immutable and immutable in self:
            raise AccessError(_(
                'You must be a member of the `Immutable` group to grant'
                ' access to it'
            ))
        return super(ResGroups, self).write(vals)
