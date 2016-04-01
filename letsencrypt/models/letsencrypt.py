# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
import logging
import urllib2
import urlparse
import subprocess
import tempfile
from openerp import _, api, models, exceptions
from openerp.tools.config import _get_default_datadir


DEFAULT_KEY_LENGTH = 4096
_logger = logging.getLogger(__name__)


class Letsencrypt(models.AbstractModel):
    _name = 'letsencrypt'
    _description = 'Abstract model providing functions for letsencrypt'

    @api.model
    def get_data_dir(self):
        return os.path.join(_get_default_datadir(), 'letsencrypt')

    @api.model
    def get_challenge_dir(self):
        return os.path.join(self.get_data_dir(), 'acme-challenge')

    @api.model
    def call_cmdline(self, cmdline, loglevel=logging.INFO,
                     raise_on_result=True):
        process = subprocess.Popen(
            cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            _logger.log(loglevel, stderr)
        if stdout:
            _logger.log(loglevel, stdout)

        if process.returncode:
            raise exceptions.Warning(
                _('Error calling %s: %d') % (cmdline[0], process.returncode),
                ' '.join(cmdline),
            )

        return process.returncode

    @api.model
    def generate_account_key(self):
        data_dir = self.get_data_dir()
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
        account_key = os.path.join(data_dir, 'account.key')
        if not os.path.isfile(account_key):
            _logger.info('generating rsa account key')
            self.call_cmdline([
                'openssl', 'genrsa', '-out', account_key,
                str(DEFAULT_KEY_LENGTH),
            ])
        assert os.path.isfile(account_key), 'failed to create rsa key'
        return account_key

    @api.model
    def generate_domain_key(self, domain):
        domain_key = os.path.join(self.get_data_dir(), '%s.key' % domain)
        if not os.path.isfile(domain_key):
            _logger.info('generating rsa domain key for %s', domain)
            self.call_cmdline([
                'openssl', 'genrsa', '-out', domain_key,
                str(DEFAULT_KEY_LENGTH),
            ])
        return domain_key

    @api.model
    def validate_domain(self, domain):
        if domain in ['localhost', '127.0.0.1'] or\
                domain.startswith('10.') or\
                domain.startswith('172.16.') or\
                domain.startswith('192.168.'):
            raise exceptions.Warning(
                _("Let's encrypt doesn't work with private addresses!"))

    @api.model
    def generate_csr(self, domain):
        domains = [domain]
        i = 0
        while self.env['ir.config_parameter'].get_param(
                'letsencrypt.altname.%d' % i):
            domains.append(
                self.env['ir.config_parameter']
                .get_param('letsencrypt.altname.%d' % i)
            )
            i += 1
        _logger.info('generating csr for %s', domain)
        if len(domains) > 1:
            _logger.info('with alternative subjects %s', ','.join(domains[1:]))
        config = self.env['ir.config_parameter'].get_param(
            'letsencrypt.openssl.cnf', '/etc/ssl/openssl.cnf')
        csr = os.path.join(self.get_data_dir(), '%s.csr' % domain)
        with tempfile.NamedTemporaryFile() as cfg:
            cfg.write(open(config).read())
            if len(domains) > 1:
                cfg.write(
                    '\n[SAN]\nsubjectAltName=' +
                    ','.join(map(lambda x: 'DNS:%s' % x, domains)) + '\n')
            cfg.file.flush()
            cmdline = [
                'openssl', 'req', '-new',
                self.env['ir.config_parameter'].get_param(
                    'letsencrypt.openssl.digest', '-sha256'),
                '-key', self.generate_domain_key(domain),
                '-subj', '/CN=%s' % domain, '-config', cfg.name,
                '-out', csr,
            ]
            if len(domains) > 1:
                cmdline.extend([
                    '-reqexts', 'SAN',
                ])
            self.call_cmdline(cmdline)
        return csr

    @api.model
    def cron(self):
        domain = urlparse.urlparse(
            self.env['ir.config_parameter'].get_param(
                'web.base.url', 'localhost')).netloc
        self.validate_domain(domain)
        account_key = self.generate_account_key()
        csr = self.generate_csr(domain)
        acme_challenge = self.get_challenge_dir()
        if not os.path.isdir(acme_challenge):
            os.makedirs(acme_challenge)
        if self.env.context.get('letsencrypt_dry_run'):
            crt_text = 'I\'m a test text'
        else:  # pragma: no cover
            from .acme_tiny import get_crt, DEFAULT_CA
            crt_text = get_crt(
                account_key, csr, acme_challenge, log=_logger, CA=DEFAULT_CA)
        with open(os.path.join(self.get_data_dir(), '%s.crt' % domain), 'w')\
                as crt:
            crt.write(crt_text)
            chain_cert = urllib2.urlopen(
                self.env['ir.config_parameter'].get_param(
                    'letsencrypt.chain_certificate_address',
                    'https://letsencrypt.org/certs/'
                    'lets-encrypt-x1-cross-signed.pem')
            )
            crt.write(chain_cert.read())
            chain_cert.close()
            _logger.info('wrote %s', crt.name)
        self.call_cmdline([
            'sh', '-c', self.env['ir.config_parameter'].get_param(
                'letsencrypt.reload_command', ''),
        ])
