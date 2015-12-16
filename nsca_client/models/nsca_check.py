# -*- coding: utf-8 -*-
# © 2015 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os
import shlex
import subprocess

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError

from openerp.addons.base.ir.ir_cron import str2tuple

_logger = logging.getLogger(__name__)

SEND_NSCA_BIN = '/usr/sbin/send_nsca'


def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


class NscaCheck(models.Model):
    _name = "nsca.check"
    _description = u"NSCA Check"
    _inherits = {'ir.cron': 'cron_id'}

    cron_id = fields.Many2one(
        'ir.cron', string=u"Cron",
        required=True, ondelete='cascade', readonly=True)
    server_id = fields.Many2one(
        'nsca.server', string=u"Server", required=True)
    service = fields.Char(u"Service", required=True)
    nsca_model = fields.Char(u"Model")
    nsca_function = fields.Char(u"Method")
    nsca_args = fields.Char(u"Arguments")

    @api.model
    def default_get(self, fields_list):
        """Set some default values on the fly, without overriding fields (which
        has the side effect to re-create the fields on the current model).
        """
        res = super(NscaCheck, self).default_get(fields_list)
        NscaServer = self.env['nsca.server']
        res['name'] = 'TEMP'    # Required on 'ir.cron', replaced later
        res['interval_number'] = 10
        res['interval_type'] = 'minutes'
        res['server_id'] = NscaServer.search([])[0].id
        return res

    @api.multi
    def _force_values(self):
        """Force some values:
            - Compute the name of the NSCA check to be readable
              among the others 'ir.cron' records.
        """
        for check in self:
            vals = {
                'name': u"%s - %s" % (_(u"NSCA Check"), check.service),
                'model': self._name,
                'function': '_cron_check',
                'args': '(%s,)' % check.id,
                'doall': False,
                'numbercall': -1
            }
            super(NscaCheck, check).write(vals)

    @api.model
    def create(self, vals):
        check = super(NscaCheck, self).create(vals)
        check._force_values()
        return check

    @api.multi
    def write(self, vals):
        res = super(NscaCheck, self).write(vals)
        if 'service' in vals:
            self._force_values()
        return res

    @api.model
    def _cron_check(self, check_id):
        self._check_send_nsca_command()
        check = self.browse(check_id)
        rc, message = 3, "Unknown"
        try:
            args = str2tuple(check.nsca_args)
            NscaModel = self.env[check.nsca_model]
            rc, message = getattr(NscaModel, check.nsca_function)(*args)
        except Exception, exc:
            rc, message = 2, "%s" % exc
            _logger.error("%s - %s", check.service, message)
        check._send_nsca(rc, message)
        return True

    @api.multi
    def _send_nsca(self, rc, message):
        """Send the result of the check to the NSCA daemon."""
        for check in self:
            check_result = self._format_check_result(check, rc, message)
            cmd = self._prepare_command(check)
            self._run_command(check, cmd, check_result)

    @api.model
    def _format_check_result(self, check, rc, message):
        """Format the check result with tabulations as delimiter."""
        message = message.replace('\t', ' ')
        hostname = self.env['ir.config_parameter'].get_param(
            'nsca_client.hostname', 'localhost')
        check_result = u"%s\t%s\t%s\t%s" % (
            hostname, check.service, rc, message)
        return check_result.encode('utf-8')

    @api.model
    def _prepare_command(self, check):
        """Prepare the shell command used to send the check result
        to the NSCA daemon.
        """
        cmd = u"/usr/sbin/send_nsca -H %s -p %s -c %s" % (
            check.server_id.name,
            check.server_id.port,
            check.server_id.config_file_path)
        return shlex.split(cmd)

    @api.model
    def _run_command(self, check, cmd, check_result):
        """Send the check result through the '/usr/sbin/send_nsca' command."""
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            stdout = proc.communicate(
                input=check_result)[0]
            _logger.info("%s: %s", check_result, stdout.strip())
        except Exception, exc:
            _logger.error(exc)

    def _check_send_nsca_command(self):
        """Check if the NSCA client is installed."""
        if not is_exe(SEND_NSCA_BIN):
            raise UserError(
                _(u"Command '%s' not found. Please install the NSCA client.\n"
                  u"On Debian/Ubuntu: apt-get install nsca-client") % (
                    SEND_NSCA_BIN))
