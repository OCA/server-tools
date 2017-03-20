# -*- coding: utf-8 -*-
# © 2016-2017 Therp BV <http://therp.nl>
# © 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
import logging
import urllib2
import urlparse
import subprocess
import tempfile

from openerp import _, api, models
from openerp.tools import config
from openerp.exceptions import Warning as UserError


DEFAULT_KEY_LENGTH = 4096
_logger = logging.getLogger(__name__)


def get_data_dir():
    return os.path.join(config.options.get('data_dir'), 'letsencrypt')


def get_challenge_dir():
    return os.path.join(get_data_dir(), 'acme-challenge')


class Letsencrypt(models.AbstractModel):
    _name = 'letsencrypt'
    _description = 'Abstract model providing functions for letsencrypt'

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
            raise UserError(
                _('Error calling %s: %d') % (cmdline[0], process.returncode),
                ' '.join(cmdline),
            )

        return process.returncode

    @api.model
    def generate_account_key(self):
        data_dir = get_data_dir()
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
        domain_key = os.path.join(get_data_dir(), '%s.key' % domain)
        if not os.path.isfile(domain_key):
            _logger.info('generating rsa domain key for %s', domain)
            self.call_cmdline([
                'openssl', 'genrsa', '-out', domain_key,
                str(DEFAULT_KEY_LENGTH),
            ])
        return domain_key

    @api.model
    def validate_domain(self, domain):
        local_domains = [
            'localhost', 'localhost.localdomain', 'localhost6',
            'localhost6.localdomain6'
        ]

        def _ip_is_private(address):
            import IPy
            try:
                ip = IPy.IP(address)
            except:
                return False
            return ip.iptype() == 'PRIVATE'

        if domain in local_domains or _ip_is_private(domain):
            raise UserError(_(
                "Let's encrypt doesn't work with private addresses "
                "or local domains!\n"
                "Check the web.base.url system parameter."
            ))

    @api.model
    def generate_csr(self, domain, ignore_altnames=False):
        domains = [domain]
        parameter_model = self.env['ir.config_parameter']
        if not ignore_altnames:
            altnames = parameter_model.search(
                [('key', 'like', 'letsencrypt.altname.')],
                order='key'
            )
            for altname in altnames:
                domains.append(altname.value)
        _logger.info('generating csr for %s', domain)
        if len(domains) > 1:
            _logger.info('with alternative subjects %s', ','.join(domains[1:]))
        config = parameter_model.get_param(
            'letsencrypt.openssl.cnf', '/etc/ssl/openssl.cnf'
        )
        csr = os.path.join(get_data_dir(), '%s.csr' % domain)
        with tempfile.NamedTemporaryFile() as cfg:
            cfg.write(open(config).read())
            if len(domains) > 1:
                cfg.write(
                    '\n[SAN]\nsubjectAltName=' +
                    ','.join(map(lambda x: 'DNS:%s' % x, domains)) + '\n')
            cfg.file.flush()
            cmdline = [
                'openssl', 'req', '-new',
                parameter_model.get_param(
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

    def _get_crt(self, csr):
        """Get certificate for csr using the acme protocol."""
        from acme_tiny import get_crt, DEFAULT_CA
        account_key = self.generate_account_key()
        acme_challenge = get_challenge_dir()
        if not os.path.isdir(acme_challenge):
            os.makedirs(acme_challenge)
        return get_crt(
            account_key,
            csr,
            acme_challenge,
            log=_logger,
            CA=DEFAULT_CA
        )

    @api.model
    def cron(self):
        save_error = None
        domain = urlparse.urlparse(
            self.env['ir.config_parameter'].get_param(
                'web.base.url', 'localhost')).hostname
        self.validate_domain(domain)
        if self.env.context.get('letsencrypt_dry_run'):
            crt_text = 'I\'m a test text'
        else:  # pragma: no cover
            csr = self.generate_csr(domain)
            try:
                crt_text = self._get_crt(csr)
            except Exception as ex:
                # If certificate renewal fails for altname, we still will
                # keep main domain with valid certificate:
                _logger.warn(
                    'Exception occured during certificate retrieval.'
                    ' Retrying without altnames. Exception was: %s' %
                    str(ex)
                )
                save_error = ex
                csr = self.generate_csr(domain, ignore_altnames=True)
                crt_text = self._get_crt(csr)
        with open(os.path.join(get_data_dir(), '%s.crt' % domain), 'w')\
                as crt:
            crt.write(crt_text)
            chain_cert = urllib2.urlopen(
                self.env['ir.config_parameter'].get_param(
                    'letsencrypt.chain_certificate_address',
                    'https://letsencrypt.org/certs/'
                    'lets-encrypt-x3-cross-signed.pem')
            )
            crt.write(chain_cert.read())
            chain_cert.close()
            _logger.info('wrote %s', crt.name)
        reload_cmd = self.env['ir.config_parameter'].get_param(
            'letsencrypt.reload_command', False)
        if reload_cmd:
            _logger.info('reloading webserver...')
            self.call_cmdline(['sh', '-c', reload_cmd])
        else:
            _logger.info('no command defined for reloading webserver, please '
                         'do it manually in order to apply new certificate')
        if save_error:
            raise UserError(
                _("Job completed, but following error was encountered: %s") %
                str(save_error)
            )
