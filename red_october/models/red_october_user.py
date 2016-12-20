# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RedOctoberUser(models.Model):

    _name = 'red.october.user'
    _description ='Red October User'

    user_id = fields.Many2one(
        string='User',
        comodel_name='res.users',
        required=True,
    )
    name = fields.Char(
        related='user_id.name',
    )
    vault_ids = fields.Many2many(
        string='Vaults',
        comodel_name='red.october.vault',
        required=True,
        default=lambda s: s._default_vault_ids(),
        domain="[('user_id.company_id', 'in', company_ids)]",
    )
    delegation_ids = fields.One2many(
        string='Delegations',
        comodel_name='red.october.delegation',
        inverse_name='user_id',
    )
    is_admin = fields.Boolean(
        string='Admin',
    )
    is_active = fields.Boolean()
    encrypt_type = fields.Selection([
        ('RSA', 'RSA'),
        ('ECC', 'ECC'),
    ],
        default='RSA',
        required=True,
    )

    _sql_constraints = [
        ('user_vaults_unique', 'UNIQUE(user_id, vault_ids)',
         'This user is already registered in this vault.'),
    ]

    @api.model
    def _default_vault_ids(self):
        return [
            (4, self.env['red.october.vault'].get_current_vault().id),
        ]

    @api.model
    def create(self, vals):
        """ It creates the user on the remote vaults. """
        already_active = vals.get('is_active')
        vals['is_active'] = True
        res = super(RedOctoberUser, self).create(vals)
        if already_active:
            return res
        for vault in self.vault_ids:
            with vault.get_api() as api:
                api.create_user()
                if res.is_admin:
                    record._update_role('admin')
        res.active = True
        return res

    @api.multi
    def update(self, vals):
        """ It updates the user on the remote vaults. """
        for record in self:
            role = None
            active = vals.get('is_active')
            is_admin = vals.get('is_admin')
            if is_admin is not None and is_admin != record.is_admin:
                role = 'admin'
            elif active is not None and active != record.active:
                role = 'revoke'
            if role:
                record._update_role(role)
        return super(RedOctoberUser, self).update(vals)

    @api.multi
    def unlink(self):
        """ It removes the user from the remote vaults. """
        self._update_role('revoke')
        return super(RedOctoberUser, self).unlink()

    @api.model
    def upsert_by_user(self, user=None, vaults=None):
        """ It returns the existing RedOctoberUser or creates a new one. """
        if user is None:
            user = self.env.user
        if vaults is None:
            vaults = user.company_id.red_october_ids
        vault_user = self.search([
            ('user_id', '=', user.id),
            ('vault_ids', 'in', vaults.ids),
        ])
        if not vault_user:
            vault_user = self.create({
                'user_id': user.id,
                'vault_ids': [(6, 0, vaults.ids)],
            })
        return vault_user

    @api.multi
    def _update_role(self):
        """ It alters the user role. """
        for record in self:
            for vault in record.vault_ids:
                with vault.get_api() as api:
                    api.modify_user_role(res.name, command=role)
