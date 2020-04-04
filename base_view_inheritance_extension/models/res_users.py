# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def unlink(self):
        """
        Finds any views assigned specifically to this user and deletes them.
        """
        self.env['ir.ui.view'].sudo().with_context(
            active_test=False,
        ).search([
            ('user_ids', 'in', self.ids)
            ]).with_context(
                active_test=True).filtered(
                    lambda x: not x.user_ids - self,
        ).unlink()
        return super(ResUsers, self).unlink()

    @api.multi
    def write(self, vals):
        """
        If a user has been set as inactive then, any views that are assigned
        to them specifically as set as inactive as well.
        """
        active = vals.get('active')
        if active is not None:
            self.env['ir.ui.view'].sudo().with_context(
                active_test=False,
            ).search([
                ('user_ids', 'in', self.ids)]).with_context(
                    active_test=True).filtered(
                        lambda x: not x.user_ids - self,
            ).write({'active': active})
        return super(ResUsers, self).write(vals)
