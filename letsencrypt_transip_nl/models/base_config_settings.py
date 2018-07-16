# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models
from tempfile import NamedTemporaryFile
import base64
import logging

_logger = logging.getLogger(__name__)

try:
    from transip.service.objects import DnsEntry
    from transip.service import DomainService
except ImportError:
    _logger.error('`transip` Python library is missing.')


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    letsencrypt_dns_provider = fields.Selection(
        selection_add=[('transip', 'TransIP')],
    )

    def letsencrypt_transip_support(self, challenge, domain):
        """ This function will be called by _respond_challenge_dns in order to
            create the DNS record on transip.nl.
        """
        ir_config_parameter = self.env['ir.config_parameter']
        login = ir_config_parameter.get_param('letsencrypt_login')
        key = ir_config_parameter.get_param('letsencrypt_key')
        url = ir_config_parameter.get_param('letsencrypt_url')
        token = base64.urlsafe_b64encode(challenge.token)
        dns_entry = DnsEntry('_acme-challenge', 86400, 'TXT', token)
        with NamedTemporaryFile() as f:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            key = serialization.load_pem_private_key(
                str(key),
                password=None,
                backend=default_backend())
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()))
            f.flush()
            # keep in mind that set_dns_entries removes all the entries and
            # inserts this one.
            DomainService(login, f.name, url).set_dns_entries(
                domain, [dns_entry])
