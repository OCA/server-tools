# -*- coding: utf-8 -*-
# Copyright 2015-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResUsers(models.Model):

    _inherit = 'res.users'

    login = fields.Char(
        'Login',
        size=64,
        required=True,
        help='Used to log into the system. Case insensitive.',
    )

    @api.model
    def search(self, domain, *args, **kwargs):
        """ Overload search to lowercase name domains. This can't be done in
        a regular search method as the field is not computed
        """
        for idx, _domain in enumerate(domain):
            if _domain[0] == 'login':
                lower = _domain[2].lower() if _domain[2] else False
                domain[idx] = (_domain[0], _domain[1], lower)
        return super(ResUsers, self).search(domain, *args, **kwargs)

    @api.model
    def create(self, vals, ):
        """ Overload create to lowercase login """
        vals['login'] = vals.get('login', '').lower()
        return super(ResUsers, self).create(vals)

    @api.multi
    def write(self, vals, ):
        """ Overload write to lowercase login """
        if vals.get('login'):
            vals['login'] = vals['login'].lower()
        return super(ResUsers, self).write(vals)
