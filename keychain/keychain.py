# -*- coding: utf-8 -*-
# © 2016 Akretion Mourad EL HADJ MIMOUNE, David BEAL, Raphaël REVERDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from functools import wraps

import logging
import json

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.tools.config import config

_logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError as err:
    _logger.debug(err)


def implemented_by_keychain(func):
    """Call a prefixed function based on 'namespace'."""
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        fun_name = func.__name__
        fun = '_%s%s' % (cls.namespace, fun_name)
        if not hasattr(cls, fun):
            fun = '_default%s' % (fun_name)
        return getattr(cls, fun)(*args, **kwargs)
    return wrapper


class KeychainAccount(models.Model):
    """Manage all accounts of external systems in one place."""

    _name = 'keychain.account'

    name = fields.Char(required=True, help="Humain readable label")
    technical_name = fields.Char(
        required=True,
        help="Technical name. Must be unique")
    namespace = fields.Selection([], help="Type of account", required=True)
    environment = fields.Char(
        required=False,
        help="'prod', 'dev', etc. or empty (for all)"
    )
    login = fields.Char(help="Login")
    clear_password = fields.Char(
        help="Password. Leave empty if no changes",
        inverse='_set_password',
        compute='_compute_password',
        store=False)
    password = fields.Char(
        help="Password is derived from clear_password",
        readonly=True)
    data = fields.Text(help="Additionnal data as json")

    def _compute_password(self):
        # Only needed in v8 for _description_searchable issues
        return True

    def get_password(self):
        """Password in clear text."""
        try:
            return self._decode_password(self.password)
        except Warning as warn:
            raise Warning(
                "%s \n"
                "Account: %s %s %s " % (
                    warn,
                    self.login, self.name, self.technical_name
                )
            )

    def get_data(self):
        """Data in dict form."""
        return self._parse_data(self.data)

    @api.constrains('data')
    def _check_data(self):
        """Ensure valid input in data field."""
        for account in self:
            if account.data:
                parsed = account._parse_data(account.data)
                if not account._validate_data(parsed):
                    raise ValidationError("Data not valid")

    def _set_password(self):
        """Encode password from clear text."""
        # inverse function
        for rec in self:
            rec.password = rec._encode_password(rec.clear_password)

    @api.model
    def retrieve(self, domain):
        """Search accounts for a given domain.

        Environment is added by this function.
        Use this instead of search to benift from environment filtering"""
        domain.append(['environment', 'in', self._retrieve_env()])
        return self.search(domain)

    @api.model
    def _retrieve_env(self):
        """Returns the current environment.

        You may override this function to fit your needs.

        returns: a tuple like:
            ('dev', 'test', False)
            Which means accounts for dev, test and blank (not set)"""
        return ("dev", False)

    @api.multi
    def write(self, vals):
        """At this time there is no namespace set."""
        if not vals.get('data') and not self.data:
            vals['data'] = self._serialize_data(self._init_data())
        return super(KeychainAccount, self).write(vals)

    @implemented_by_keychain
    def _validate_data(self, data):
        pass

    @implemented_by_keychain
    def _init_data(self):
        pass

    @staticmethod
    def _serialize_data(data):
        return json.dumps(data)

    @staticmethod
    def _parse_data(data):
        try:
            return json.loads(data)
        except ValueError:
            raise ValidationError("Data not valid JSON")

    @classmethod
    def _encode_password(cls, data):
        cipher = cls._get_cipher()
        return cipher.encrypt(str((data or '').encode('UTF-8')))

    @classmethod
    def _decode_password(cls, data):
        cipher = cls._get_cipher()
        try:
            return unicode(cipher.decrypt(str(data)), 'UTF-8')
        except InvalidToken:
            raise Warning(
                "Password has been encrypted with a different "
                "key. Unless you can recover the previous key, "
                "this password unreadable."
            )

    @staticmethod
    def _get_cipher():
        try:
            key = config['keychain_key']
        except:
            raise Warning(
                "No 'keychain_key' entry found in config file. "
                "Use a key like : %s" % Fernet.generate_key()
            )
        return Fernet(key)
