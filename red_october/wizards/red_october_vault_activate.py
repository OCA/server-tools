# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class RedOctoberVaultActivate(models.TransientModel):

    _name = 'red.october.vault.activate'
    _description = 'Red October Vault Activation'

    is_active = fields.Boolean(
        string='Already Active',
        help='Check this if the vault has already been activated.',
    )
    root_user_id = fields.Many2one(
        string='Admin User',
        comodel_name='res.users',
        default=lambda s: s.env.ref('base.user_root'),
        required=True,
        help="The vault's admin user will be assigned to this Odoo user.",
    )
    vault_ids = fields.Many2many(
        string='Vaults',
        comodel_name='red.october.vault',
        required=True,
        default=lambda s: s._default_vault_ids(),
        domain="[('is_active', '=', False)]",
    )
    admin_user_id = fields.Many2one(
        string='Admin User',
        comodel_name='red.october.user',
        required=True,
        context="{'default_user_id': root_user_id,"
                " 'default_vault_ids': vault_ids,"
                " 'default_is_admin': True,"
                " 'default_is_active': True,"
                " }",
    )
    admin_password = fields.Char(
        computed='_compute_admin_password',
        inverse='_inverse_admin_password',
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
    def _compute_admin_password(self):
        """ It passes because there isn't actually data. """
        pass

    @api.multi
    def _inverse_admin_password(self):
        """ It doesn't save any data, but allows the password in cache. """
        pass

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
        assert self.admin_password
        assert not self.is_active
        _logger.debug('Activating vaults %s' % self.vault_ids)
        for vault in self.vault_ids:
            with vault.get_api(self.admin_user_id,
                               self.admin_password) as api:
                _logger.debug('Creating vault with %s' % api)
                api.create_vault()
                vault.active = True