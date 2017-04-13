# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RedOctoberDelegation(models.Model):

    _name = 'red.october.delegation'
    _description = 'Red October Delegation'

    CONTEXT_SKIP = 'ro_no_delegate'

    vault_id = fields.Many2one(
        string='Vault',
        comodel_name='red.october.vault',
        required=True,
    )
    user_id = fields.Many2one(
        string='User',
        comodel_name='red.october.user',
        required=True,
    )
    date_expire = fields.Datetime(
        string='Expire Date',
        help='Date that this delegation will expire.',
    )
    num_expire = fields.Integer(
        string='Expire Uses',
        help='Amount of uses until this delegation will expire.',
    )
    delta_expire = fields.Binary(
        compute='_compute_delta_expire',
    )
    active = fields.Boolean(
        store=True,
        compute='_compute_active',
    )

    @api.multi
    @api.depends('date_expire')
    def _compute_delta_expire(self):
        now = datetime.now()
        for record in self:
            expire = fields.Datetime.from_string(record.date_expire)
            record.delta_expire = expire - now

    @api.multi
    @api.depends('date_expire', 'num_expire')
    def _compute_active(self):
        for record in self:
            record.active = all((
                record.num_expire, record.delta_expire.total_seconds() > 0
            ))

    @api.multi
    def delegate(self, password):
        """ It runs a remote delegation & deactivates existing active locals.

        Any existing locals are deactivated because a vault can only maintain
        one active delegation per user.
        
        Args:
            password (str): Password for the associated Red October user.
        """
        if self._context.get(self.CONTEXT_SKIP):
            return False
        for record in self:
            with record.vault_id.get_api(record.user_id, password) as api:
                api.delegate(
                    record.delta_expire, record.num_expire,
                )
            existing = self.search([
                ('active', '=', True),
                ('vault_id', '=', record.vault_id.id),
                ('user_id', '=', record.user_id.id),
                ('id', '!=', record.id),
            ])
            if existing:
                existing.write({
                    'date_expire': fields.Datetime.now(),
                })
        return True

    @api.multi
    def decrement(self, amount=1):
        """ It decrements the delegation num_expire by amount. """
        for record in self:
            record.write({
                'num_expire': record.num_expire - amount,
            })
