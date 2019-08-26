import base64

from odoo import models, api
from lxml.objectify import fromstring


class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    @api.model
    def _get_eval_context(self, action=None):
        eval_context = super(IrActionsServer, self)._get_eval_context(
            action=action)

        if self._context.get('active_model') == 'account.invoice':
            eval_context.update({
                'fromstring': fromstring,
                'base64': base64
            })
        return eval_context
