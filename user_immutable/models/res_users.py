# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import AccessError

from .res_groups import IMMUTABLE


class ResUsers(models.Model):

    _inherit = 'res.users'

    def _check_immutable(self):
        """ Check to see if the user being edited is Immutable and if so,
        make sure that the user performing the action has access
        """
        if self.has_group(IMMUTABLE):
            if not self.env.user.has_group(IMMUTABLE):
                raise AccessError(
                    _('You do not have permission to alter an Immutable User')
                )

    @api.multi
    def write(self, vals):
        """ Override write to verify that there are no alterations to users
        whom are members of the `Immutable` group
        """
        for rec in self:
            rec._check_immutable()
        immutable = self.env.ref(IMMUTABLE)
        has_group = self.env.user.has_group(IMMUTABLE)
        if vals.get('in_group_%s' % immutable.id) and not has_group:
            raise AccessError(
                _('You must be a member of the `Immutable` group to grant '
                  'access to it')
            )
        return super(ResUsers, self).write(vals)

    @api.multi
    def unlink(self):
        """ Override unlink to verify that there are no deletions of users
        whom are members of the `Immutable` group
        """
        for rec in self:
            rec._check_immutable()
        return super(ResUsers, self).unlink()
