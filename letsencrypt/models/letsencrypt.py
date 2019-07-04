# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# © 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta
from os.path import join, isdir, isfile
from os import makedirs
from odoo import _, api, models, exceptions
from odoo.tools import config
import logging
import urlparse
import subprocess
import requests
import base64
import os
import re

_logger = logging.getLogger(__name__)

try:
    from cryptography.hazmat.backends import default_backend
    import josepy as jose
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization, hashes
    from acme import client, crypto_util, errors
    from acme.messages import Registration, NewRegistration, \
        RegistrationResource
    from acme import challenges
    import IPy
except ImportError as e:
    _logger.debug(e)


WILDCARD = '*.'  # as defined in the spec
DEFAULT_KEY_LENGTH = 4096
TYPE_CHALLENGE_HTTP = 'http-01'
TYPE_CHALLENGE_DNS = 'dns-01'
V2_STAGING_DIRECTORY_URL = \
    'https://acme-staging-v02.api.letsencrypt.org/directory'
V2_DIRECTORY_URL = 'https://acme-v02.api.letsencrypt.org/directory'


def _get_data_dir():
    return join(config.options.get('data_dir'), 'letsencrypt')


def _get_challenge_dir():
    return join(_get_data_dir(), 'acme-challenge')


class Letsencrypt(models.AbstractModel):
    _name = 'letsencrypt'
    _description = 'Abstract model providing functions for letsencrypt'

    @api.model
    def _generate_key(self, key_name):
        _logger.info('Generating key ' + str(key_name))
        data_dir = _get_data_dir()
        if not isdir(data_dir):
            makedirs(data_dir)
        key_file = join(data_dir, key_name)
        if not isfile(key_file):
            _logger.info('Generating a new key')
            key_json = jose.JWKRSA(key=jose.ComparableRSAKey(
                rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=DEFAULT_KEY_LENGTH,
                    backend=default_backend())))
            key = key_json.key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption())
            with open(key_file, 'wb') as _file:
                _file.write(key)
        return key_file

    @api.model
    def _validate_domain(self, domain):
        local_domains = [
            'localhost', 'localhost.localdomain', 'localhost6',
            'localhost6.localdomain6'
        ]

        def _ip_is_private(address):
            try:
                ip = IPy.IP(address)
            except ValueError:
                return False
            return ip.iptype() == 'PRIVATE'

        if domain in local_domains or _ip_is_private(domain):
            raise exceptions.Warning(
                _("Let's encrypt doesn't work with private addresses "
                    "or local domains!"))

    @api.model
    def _cron(self):
        ir_config_parameter = self.env['ir.config_parameter']
        domain = urlparse.urlparse(
            self.env['ir.config_parameter'].get_param(
                'web.base.url', 'localhost')).netloc
        self._validate_domain(domain)
        # Generate account key
        account_key_file = self._generate_key('account.key')
        account_key = jose.JWKRSA.load(open(account_key_file).read())
        # Generate domain key
        domain_key_file = self._generate_key(domain)
        client = self._create_client(account_key)
        new_reg = NewRegistration(
            key=account_key.public_key(),
            terms_of_service_agreed=True)
        try:
            client.new_account(new_reg)
        except errors.ConflictError as e:
            reg = Registration(key=account_key.public_key())
            reg_res = RegistrationResource(
                body=reg,
                uri=e.location,
            )
            client.query_registration(reg_res)
        csr = self._make_csr(account_key, domain_key_file, domain)
        authzr = client.new_order(csr)
        auth_responded = False
        for authorizations in authzr.authorizations:
            for challenge in sorted(
                    authorizations.body.challenges,
                    key=lambda x: x.chall.typ == TYPE_CHALLENGE_HTTP,
                    reverse=True):
                if challenge.chall.typ == TYPE_CHALLENGE_HTTP:
                    self._respond_challenge_http(challenge, account_key)
                    client.answer_challenge(
                        challenge,
                        challenges.HTTP01Response())
                    auth_responded = True
                    break
                elif challenge.chall.typ == TYPE_CHALLENGE_DNS:
                    self._respond_challenge_dns(
                        challenge,
                        account_key,
                        authorizations.body.identifier.value,
                    )
                    client.answer_challenge(
                        challenge, challenges.DNSResponse())
                    auth_responded = True
                    break
        if not auth_responded:
            raise exceptions.ValidationError(
                _('Could not respond to letsencrypt challenges.'))
        # let them know we are done and they should check
        deadline = datetime.now() + timedelta(
            minutes=int(
                ir_config_parameter.get_param('letsencrypt_backoff', 3)))
        order_resource = client.poll_and_finalize(authzr, deadline)
        with open(join(_get_data_dir(), '%s.crt' % domain), 'w') as crt:
            crt.write(order_resource.fullchain_pem)
            _logger.info('SUCCESS: Certificate saved :%s', crt.name)
            reload_cmd = ir_config_parameter.get_param(
                'letsencrypt.reload_command', False)
            if reload_cmd:
                self._call_cmdline(['sh', '-c', reload_cmd])
            else:
                _logger.warning("No reload command defined.")

    def _create_client(self, account_key):
        net = client.ClientNetwork(account_key)
        if config['test_enable']:
            directory_url = V2_STAGING_DIRECTORY_URL
        else:
            directory_url = V2_DIRECTORY_URL
        directory_json = requests.get(directory_url).json()
        return client.ClientV2(directory_json, net)

    def _cascade_domains(self, altnames):
        """ Given an list of domains containing one or more wildcard domains
        the following are performed:
            1)  for every wildcard domain:
                    a) gets the index of it's wildcard characters
                    b) if there are non wildcard domain names that are the same
                    after the index of the current wildcard name remove them.
            2)  when done, return the modified altnames
        """
        for altname in filter(lambda x: WILDCARD in x, altnames):
            pat = re.compile('^.*' + altname.replace(WILDCARD, '') + '.*$')
            for _altname in filter(lambda x: WILDCARD not in x, altnames):
                if pat.search(_altname):
                    altnames.remove(_altname)
        return altnames

    def _make_csr(self, account_key, domain_key_file, domain):
        parameter_model = self.env['ir.config_parameter']
        altnames = parameter_model.get_param('letsencrypt_altnames')
        if altnames:
            altnames = re.split(',|\n| |;', altnames)
            valid_domains = altnames + [domain]
            valid_domains = self._cascade_domains(valid_domains)
        else:
            valid_domains = [domain]
        _logger.info(
            'Making CSR for the following domains: ' + str(valid_domains))
        return crypto_util.make_csr(
            open(domain_key_file).read(), valid_domains)

    def _respond_challenge_http(self, challenge, account_key):
        """
        Respond to the HTTP challenge by writing the file to serve.
        """
        challenge_dir = _get_challenge_dir()
        if not isdir(challenge_dir):
            makedirs(challenge_dir)
        token = base64.urlsafe_b64encode(challenge.token)
        challenge_file = join(_get_challenge_dir(), '%s' % token.rstrip('='))
        with open(challenge_file, 'wb') as challenge_file:
            challenge_file.write(token.rstrip('=') + '.' + jose.b64encode(
                account_key.thumbprint(hash_function=hashes.SHA256)).decode())

    def _respond_challenge_dns(self, challenge, account_key, domain):
        """
        Respond to the DNS challenge by creating the DNS record
        on the provider.
        """
        letsencrypt_dns_function = '_respond_challenge_dns_' + \
            self.env['ir.config_parameter'].get_param(
                'letsencrypt_dns_provider')
        getattr(self, letsencrypt_dns_function)(challenge, account_key, domain)

    @api.model
    def _call_cmdline(self, cmdline, env=None, shell=False):
        process = subprocess.Popen(
            cmdline,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            shell=shell,
        )
        stdout, stderr = process.communicate()
        if process.returncode:
            raise exceptions.Warning(_(
                'Error calling %s: %s %s %s' % (
                    cmdline,
                    str(process.returncode) + ' '.join(cmdline),
                    stdout,
                    stderr,
                )))

    @api.model
    def _respond_challenge_dns_shell(self, challenge, account_key, domain):
        script_str = self.env['ir.config_parameter'].get_param(
            'letsencrypt_script')
        if script_str:
            env = os.environ
            env.update(
                LETSENCRYPT_DNS_CHALLENGE=jose.encode_b64jose(
                    challenge.chall.token),
                LETSENCRYPT_DNS_DOMAIN=domain,
            )
            self.env['letsencrypt']._call_cmdline(
                script_str,
                env=env,
                shell=True,
            )
