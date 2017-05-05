# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from odoo.exceptions import AccessError

IMMUTABLE = 'user_immutable.group_immutable'


class ResGroups(models.Model):

    _inherit = 'res.groups'

    @api.multi
    def write(self, vals):
        """ Override write to verify that access to the `Immutable` group is
        not given or removed by users without access """
        immutable_id = -1
        try:
            immutable_id = self.env.ref(IMMUTABLE).id
        except ValueError:
            pass
        if self.id == immutable_id and vals.get('users'):
            if not self.env.user.has_group(IMMUTABLE):
                raise AccessError(
                    'You must be a member of the `Immutable` group to grant '
                    'access to it'
                )
        return super(ResGroups, self).write(vals)
