# -*- coding: utf-8 -*-
# © 2016 Akretion Sebastien Beau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.config import config


class KeychainBackend(models.AbstractModel):
    _name = 'keychain.backend'
    _backend_name = None

    name = fields.Char(required=True)
    password = fields.Char(
        compute="_compute_password",
        inverse="_inverse_password",
        required=True)
    data = fields.Serialized(
        compute="_compute_keychain",
        inverse="_inverse_keychain",
        help="Additionnal data as json")

    @api.multi
    def _get_technical_name(self):
        self.ensure_one()
        return '%s,%s' % (self._name, self.id)

    @api.multi
    def _get_existing_keychain(self):
        self.ensure_one()
        return self.env['keychain.account'].retrieve([
            ('namespace', '=', self._backend_name),
            ('technical_name', '=', self._get_technical_name())
        ])

    @api.multi
    def _prepare_keychain(self):
        self.ensure_one()
        env = config.get('running_env')
        return {
            'name': "%s %s" % (self.name, env),
            'technical_name': self._get_technical_name(),
            'namespace': self._backend_name,
            'environment': env,
        }

    @api.multi
    def _get_keychain_account(self):
        self.ensure_one()
        account = self._get_existing_keychain()
        if not account:
            vals = self._prepare_keychain()
            account = self.env['keychain.account'].create(vals)
        return account

    @api.multi
    def _inverse_password(self):
        for record in self:
            account = self._get_keychain_account()
            if record.password and record.password != '******':
                account.clear_password = record.password

    @api.multi
    def _compute_password(self):
        for record in self:
            account = record._get_existing_keychain()
            if account and account.password:
                record.password = "******"
            else:
                record.password = ""

    @api.multi
    def _inverse_keychain(self):
        for record in self:
            account = record._get_keychain_account()
            account.data = account._serialize_data(record.data)

    @api.multi
    def _compute_keychain(self):
        for record in self:
            account = record._get_existing_keychain()
            if account:
                record.data = account.get_data()
            else:
                record.data = {}
