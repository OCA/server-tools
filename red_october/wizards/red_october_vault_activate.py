# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class RedOctoberVaultActivate(models.TransientModel):

    _name = 'red.october.vault.activate'
    _description = 'Red October Vault Activation'

    is_active = fields.Boolean(
        string='Already Active',
        help='Check this if the vault has already been activated.',
    )
    vault_ids = fields.Many2many(
        string='Vaults',
        comodel_name='red.october.vault',
        required=True,
        default=lambda s: s._default_vault_ids(),
        domain="[('is_active', '=', False)]",
    )
    admin_user_id = fields.Many2one(
        string='Red October User',
        comodel_name='red.october.user',
        required=True,
        context="{'default_vault_ids': vault_ids,"
                " 'default_is_admin': True,"
                " 'default_is_active': True,"
                " }",
    )
    admin_password = fields.Char(
        required=True,
    )
    admin_password_confirm = fields.Char(
        required=True,
    )

    @api.model
    def _default_vault_ids(self):
        if not self.env.context.get('active_model') == 'red.october.vault':
            return
        return [(6, 0, self.env.context.get('active_ids', []))]

    @api.multi
    def _check_vault_ids(self):
        """ It should not allow active vaults. """
        for record in self:
            if len(record.vault_ids.filtered(lambda r: r.is_active)):
                raise ValidationError(_(
                    'Cannot reinitialize a vault.'
                ))

    @api.multi
    def action_save(self):
        for record in self:
            if not record.is_active:
                record.activate_vault()
            if self.env.user != record.admin_user_id.user_id:
                self.env['red.october.user'].upsert_by_user(
                    vaults=record.vault_ids,
                )

    @api.multi
    def activate_vault(self):
        """ It activates a vault with the given admin user and password. """
        self.ensure_one()
        if self.admin_password != self.admin_password_confirm:
            raise ValidationError(_(
                'Passwords do not match.',
            ))
        if self.is_active:
            self.vault_ids.write({
                'is_active': True,
            })
            self.unlink()
            return
        for vault in self.vault_ids:
            vault.activate(self.admin_user_id, self.admin_password)
        self.unlink()
