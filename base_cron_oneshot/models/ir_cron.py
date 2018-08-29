# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _inherit = 'ir.cron'

    oneshot = fields.Boolean(
        string='Single use',
        default=False,
        help='Enable this to run the cron only once. '
             'The cron will be deleted right after execution.'
    )

    @api.model
    def create(self, vals):
        if vals.get('oneshot'):
            vals.update(self._oneshot_defaults(**vals))
        return super().create(vals)

    def _oneshot_defaults(
            self, name=None, delay=('minutes', 10), nextcall=None, **kw):
        if nextcall is None:
            nextcall = fields.Datetime.to_string(
                datetime.now() + timedelta(**dict([delay, ]))
            )
        return {
            'state': 'code',
            # TODO: shall we enforce `doall` too?
            # enforce numbercall
            'numbercall': 1,
            # make sure name is automatic
            'name': self._oneshot_make_name(name),
            'nextcall': nextcall,
        }

    def _oneshot_make_name(self, name=None):
        name = ' ' + (name if name else '')
        return '{}{}'.format(
            self.env['ir.sequence'].next_by_code('cron.oneshot'), name
        )

    @api.model
    def schedule_oneshot(self, model_name, method=None, code=None,
                         delay=('minutes', 10), **kw):
        """Create a one shot cron.

        :param model_name: a string matching an odoo model name
        :param method: an existing method to call on the model
        :param code: custom code to run on the model
        :param delay: timedelta compat values for delay as tuple
        :param kw: custom values for the cron
        """
        assert method or code, _('Provide a method or some code!')
        if method and not code:
            code = 'model.{}()'.format(method)
        model = self.env['ir.model']._get(model_name)
        vals = {
            'model_id': model.id,
            'code': code,
        }
        vals.update(self._oneshot_defaults(delay=delay))
        vals.update(kw)
        # make sure is a oneshot cron ;)
        vals['oneshot'] = True
        return self.create(vals)

    def _oneshot_cleanup_domain(self):
        # TODO: any better way to select them?
        return [
            ('oneshot', '=', True),
            ('numbercall', '=', 0),  # already executed
            ('active', '=', False),  # already executed and numbercall=0
        ]

    @api.model
    def cron_oneshot_cleanup(self):
        self.with_context(
            active_test=False
        ).search(self._oneshot_cleanup_domain()).unlink()
