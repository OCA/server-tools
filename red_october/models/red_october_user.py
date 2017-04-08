# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, fields, models
from odoo.http import request
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class RedOctoberUser(models.Model):

    _name = 'red.october.user'
    _description ='Red October User'

    SESSION_USER_ATTR = 'ro_uid'

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

    @api.model
    def _default_vault_ids(self):
        return [
            (6, 0, self.env['red.october.vault'].get_current_vault().ids),
        ]

    @api.multi
    @api.constrains('user_id', 'vault_ids')
    def _check_user_id_vault_ids(self):
        for record in self:
            results = self.search([
                ('user_id', '=', record.user_id.id),
                ('vault_ids', 'in', record.vault_ids.ids),
            ])
            if len(results) > 1:
                raise ValidationError(_(
                    'This user is already registered in this vault.',
                ))

    @api.model
    def create(self, vals):
        """ It creates the user on the remote vaults. """
        already_active = vals.get('is_active')
        vals['is_active'] = True
        res = super(RedOctoberUser, self).create(vals)
        if already_active:
            return res
        for vault in res.vault_ids:
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
    def change_current_user(self, ro_user_id):
        """ It changes the current session user to the provided.

        Args:
            ro_user_id (int): ID of the RedOctoberUser to add as the current
                session default.
        """
        setattr(request.session, self.SESSION_USER_ATTR, ro_user_id)

    @api.multi
    def change_password(self, old_passwd, new_passwd, confirm_passwd):
        """ It changes the password for the user singleton. """
        self.ensure_one()
        if new_passwd != confirm_passwd:
            raise ValidationError(_(
                'The new password and confirmation do not match. Please '
                'try again.',
            ))
        user = self.get_current_user()
        for vault in self.vault_ids:
            with vault.get_api(user, old_passwd) as api:
                api.change_password(new_passwd)
        return True

    @api.model
    def get_current_user(self):
        """ It returns the RedOctoberUser that the session user is using.

        This method currently returns the default selected in the user, but
        plans are to allow for the control of this via session.

        Returns:
            RecOctoberUser: The user that is currently in use for this
                session.
        """
        user = None
        try:
            user = self.browse(
                getattr(request.session, self.SESSION_USER_ATTR),
            )
        except AttributeError:
            pass
        if not user:
            user = self.upsert_by_user()
        return user

    @api.model
    def read_current_user(self):
        user = self.get_current_user()
        return user and user.read() or {}

    @api.model
    def get_user_profiles(self):
        """ It returns the current user's profiles. """
        users = self.search([
            ('user_id', '=', self.env.user.id),
        ])
        return users

    @api.model
    def read_user_profiles(self):
        users = self.get_user_profiles()
        return users.read()

    @api.model
    def upsert_by_user(self, user=None, vaults=None):
        """ It returns the existing RedOctoberUser or creates a new one. """
        if user is None:
            user = self.env.user
        if vaults is None:
            vaults = user.company_id.red_october_ids
        if not vaults:
            _logger.debug(
                'No vault was selected, and no default vault exists '
                'for your company.'
            )
            return
        domain = [
            ('user_id', '=', user.id),
            ('vault_ids', 'in', vaults.ids),
        ]
        vault_user = self.search(domain)
        if not vault_user:
            vault_user = self.create({
                'user_id': user.id,
                'vault_ids': [(6, 0, vaults.ids)],
            })
        return vault_user

    @api.multi
    def _update_role(self, user=None, passwd=None):
        """ It alters the user role. """
        for record in self:
            for vault in record.vault_ids:
                with vault.get_api(user, passwd) as api:
                    api.modify_user_role(res.name, command=role)
