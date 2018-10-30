# (Copyright) 2015 ABF OSIELL <http://osiell.com>
# (Copyright) 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


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
        self.env['nsca.server']._check_send_nsca_command()
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
        for check in self:
            check.server_id._send_nsca(check.service, rc, message, performance)
