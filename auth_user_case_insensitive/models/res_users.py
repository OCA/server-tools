# -*- coding: utf-8 -*-
# Copyright 2015-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import collections
from odoo import api, fields, models


class ResUsers(models.Model):

    _inherit = 'res.users'

    login = fields.Char(
        help='Used to log into the system. Case insensitive.',
    )

    @classmethod
    def _login(cls, db, login, password):
        """ Overload _login to lowercase the `login` before passing to the
        super """
        login = login.lower()
        return super(ResUsers, cls)._login(db, login, password)

    @api.model
    def create(self, vals):
        """ Overload create to lowercase login """
        vals['login'] = vals.get('login', '').lower()
        return super(ResUsers, self).create(vals)

    @api.multi
    def write(self, vals):
        """ Overload write to lowercase login """
        if vals.get('login'):
            vals['login'] = vals['login'].lower()
        return super(ResUsers, self).write(vals)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Modifies all search domains to replace login with login.lower()."""
        new_args = []
        for arg in args:
            new_arg = arg
            if len(arg) == 3 and arg[0] == 'login':
                new_rvalue = arg[2]
                if hasattr(arg[2], 'lower'):
                    new_rvalue = arg[2].lower()
                elif isinstance(arg[2], collections.Iterable):
                    new_rvalue = [getattr(
                        x, 'lower', lambda: x)() for x in arg[2]]
                new_arg = (new_arg[0], new_arg[1], new_rvalue)
            new_args.append(new_arg)
        return super(ResUsers, self).search(
            args=new_args, offset=offset, limit=limit,
            order=order, count=count)
