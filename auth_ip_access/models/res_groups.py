# coding: utf-8
# Copyright 2020 Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ResGroups(models.Model):
    _inherit = 'res.groups'

    @api.multi
    def write(self, vals):
        """ Invalidate the cache when some group's users are modified """
        if 'users' in vals:
            self.env['ip.access.rule']._clear_caches()
        return super(ResGroups, self).write(vals)
