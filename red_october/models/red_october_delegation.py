# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime

from odoo import api, fields, models


class RedOctoberDelegation(models.Model):

    _name = 'red.october.delegation'
    _description = 'Red October Delegation'

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
    @api.depends('delta_expire', 'num_expire')
    def _compute_active(self):
        for record in self:
            record.active = any((
                record.num_expire, record.delta_expire.total_seconds() > 0
            ))

    @api.model
    def create(self, vals):
        """ It creates the delegations on the remote.

        This also deactivates any existing delegations for the user.
        """
        record = super(RedOctoberDelegation, self).create(vals)
        record.delegate()
        return record

    @api.multi
    def update(self, vals):
        """ It updates the delegations on the remote. """
        res = super(RedOctoberDelegation, self).update(vals)
        self.delegate()
        return res

    @api.multi
    def delegate(self):
        """ It runs a remote delegation & deactivates existing active locals.

        The existing locals are deactivated because a vault can only maintain
        one active delegation per user.
        """
        for record in self:
            with record.vault_id.get_api() as api:
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
                existing.write({'date_expire': fields.Datetime.now()})
