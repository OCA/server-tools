# (Copyright) 2015 ABF OSIELL <http://osiell.com>
# (Copyright) 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os
import shlex
import subprocess

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

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
    allow_void_result = fields.Boolean(
        u"Allow void result", default=False,
        help=u"By default, a CRITICAL message is sent if the method does not "
             u"return.\nIf checked, no message will be sent in such a case.")

    @api.model
    def default_get(self, fields_list):
        """Set some default values on the fly, without overriding fields (which
        has the side effect to re-create the fields on the current model).
        """
        res = super(NscaCheck, self).default_get(fields_list)
        res['name'] = 'TEMP'  # Required on 'ir.cron', replaced later
        res['interval_number'] = 10
        res['interval_type'] = 'minutes'
        return res

    @api.multi
    def _force_values(self):
        """Force some values:
            - Compute the name of the NSCA check to be readable
              among the others 'ir.cron' records.
        """
        model = self.env['ir.model'].search([('model', '=', self._name)])
        for check in self:
            vals = {
                'name': u"%s - %s" % (_(u"NSCA Check"), check.service),
                'model_id': model.id,
                'state': 'code',
                'code': 'model._cron_check(%s,)' % check.id,
                'doall': False,
                'numbercall': -1
            }
            super(NscaCheck, check).write(vals)

    @api.model
    def create(self, vals):
        if not vals.get('model_id', False):
            vals['model_id'] = self.env['ir.model'].search([
                ('model', '=', self._name)]).id
        if not vals.get('state', False):
            vals['state'] = 'code'
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
        rc, message, performance = 3, "Unknown", {}
        try:
            NscaModel = self.env[check.nsca_model]
            results = {'model': NscaModel}
            safe_eval(
                'result = model.%s(%s)' % (
                    check.nsca_function, check.nsca_args or ''),
                results, mode="exec", nocopy=True)
            result = results['result']
            if not result:
                if check.allow_void_result:
                    return False
                raise ValueError(
                    "'%s' method does not return" % check.nsca_function)
            if len(result) == 2:
                rc, message = result
            else:
                rc, message, performance = result
        except Exception as exc:
            rc, message = 2, "%s" % exc
            _logger.warning("%s - %s", check.service, message)
        check._send_nsca(rc, message, performance)
        return True

    @api.multi
    def _send_nsca(self, rc, message, performance):
        """Send the result of the check to the NSCA daemon."""
        for check in self:
            msg = message
            if len(performance) > 0:
                msg += '| ' + ''.join(
                    ["%s=%s%s;%s;%s;%s;%s" % (
                        key,
                        performance[key]['value'],
                        performance[key].get('uom', ''),
                        performance[key].get('warn', ''),
                        performance[key].get('crit', ''),
                        performance[key].get('min', ''),
                        performance[key].get('max', ''),
                    ) for key in sorted(performance)])
            check_result = self._format_check_result(check, rc, msg)
            cmd = self._prepare_command(check)
            self._run_command(check, cmd, check_result)

    @api.model
    def _format_check_result(self, check, rc, message):
        """Format the check result with tabulations as delimiter."""
        message = message.replace('\t', ' ')
        hostname = check.server_id.node_hostname
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
            _logger.debug("%s: %s", check_result, stdout.strip())
        except Exception as exc:
            _logger.error(exc)

    def _check_send_nsca_command(self):
        """Check if the NSCA client is installed."""
        if not is_exe(SEND_NSCA_BIN):
            raise UserError(
                _(u"Command '%s' not found. Please install the NSCA client.\n"
                  u"On Debian/Ubuntu: apt-get install nsca-client") % (
                    SEND_NSCA_BIN))
