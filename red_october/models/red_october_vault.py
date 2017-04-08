# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from contextlib import contextmanager

from odoo import _, api, fields, models
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    from red_october import RedOctober
except ImportError:
    _logger.info('red_october Python library not installed.')


class RedOctoberVault(models.Model):

    _name = 'red.october.vault'
    _description = 'Red October Vault'

    name = fields.Char(
        compute='_compute_name',
        store=True,
    )
    host = fields.Char(
        required=True,
        help='Host or IP of Red October server.',
    )
    port = fields.Integer(
        required=True,
        default=8080,
        help='Port to use for connection.',
    )
    is_active = fields.Boolean(
        help='Vault is initialized.',
        readonly="True",
    )
    verify_cert = fields.Boolean(
        default=True,
    )
    user_ids = fields.Many2many(
        string='Vault Users',
        comodel_name='red.october.user',
        domain="[('user_id.company_id', 'in', company_ids)]",
    )
    delegation_ids = fields.One2many(
        string='Delegations',
        comodel_name='red.october.delegation',
        inverse_name='vault_id',
    )
    company_ids = fields.Many2many(
        string='Companies',
        comodel_name='res.company',
        required=True,
        default=lambda s: [(4, s.env.user.company_id.id)],
    )

    _sql_constraints = [
        ('host_port_unique', 'UNIQUE(host, port)',
         'A vault has already been created for this remote server.'),
    ]

    @api.multi
    @api.depends('host', 'port')
    def _compute_name(self):
        for record in self:
            record.name = '%s:%s' % (record.host, record.port)

    @api.multi
    def activate(self, user, password):
        """ It activates a vault with the given admin user and password.

        Args:
            user (RedOctoberUser): User for session. Set to
                :type:`None` to use the current session user.
            password (str): Password for session. Set to
                :type:`None` to use the current session password.
        """
        _logger.debug('Activate vault with %s, %s', user, password)
        self.ensure_one()
        if self.is_active:
            raise ValidationError(_(
                'A vault cannot be reactivated.',
            ))
        if not user.is_admin and len(user.vault_ids):
            raise ValidationError(_(
                'This profile is already assigned to a vault, but is not '
                'an admin. Please use another profile.',
            ))
        with self.get_api(user, password) as api:
            _logger.debug('Creating vault with %s' % api)
            api.create_vault()
            self.is_active = True
            user.write({
                'is_admin': True,
                'vault_ids': [(4, self.id)]
            })

    @api.multi
    @contextmanager
    def get_api(self, user=None, password=None):
        """ It returns a RedOctober instance, logged in with credentials.

        If no user/pass is provided, the credentials from the current session
        will be used.

        Args:
            user (RedOctoberUser, optional): User for session. Set to
                :type:`None` to use the current session user.
            password (str, optional): Password for session. Set to
                :type:`None` to use the current session password.
        Returns:
            RedOctober: Remote Red October instance, logged in with provided
                credentials.
        """
        self.ensure_one()
        if not user:
            user = self.get_current_user()
        if not password:
            password = request.session.password
        try:
            conn = RedOctober(
                self.host, self.port, user.name, password,
                verify=self.verify_cert,
            )
            _logger.debug('Red October with %s, %s', user.name, password)
            yield conn
        finally:
            pass

    @api.model_cr_context
    def get_current_vault(self):
        """ It returns the vault that the session user is currently using.

        This method currently returns the default company vault, but plans
        are to allow for the control of this via session.

        Returns:
            RecOctoberVault: The vault that is currently in use for this
                session.
        """
        user = self.env['res.users'].browse(request.session.uid)
        return user.company_id.default_red_october_id

    @api.model_cr_context
    def get_current_user(self):
        """ It returns the RedOctoberUser that the session user is using.

        This method currently returns the default selected in the user, but
        plans are to allow for the control of this via session.

        Returns:
            RecOctoberUser: The user that is currently in use for this
                session.
        """
        return self.env['red.october.user'].get_current_user()
