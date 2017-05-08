# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, models
from odoo.exceptions import AccessError

logger = logging.getLogger(__name__)
IMMUTABLE = 'user_immutable.group_immutable'


class ResGroups(models.Model):

    _inherit = 'res.groups'

    @api.multi
    def write(self, vals):
        """ Override write to verify that access to the `Immutable` group is
        not given or removed by users without access
        """
        immutable_id = -1
        try:
            immutable_id = self.env.ref(IMMUTABLE).id
        except ValueError:
            logger.info('ValueError raised due to `Immutable` group not yet '
                        'having been created')
        for rec in self:
            if rec.id == immutable_id and vals.get('users'):
                if not self.env.user.has_group(IMMUTABLE):
                    raise AccessError(
                        _('You must be a member of the `Immutable` group to '
                          'grant access to it')
                    )
        return super(ResGroups, self).write(vals)
