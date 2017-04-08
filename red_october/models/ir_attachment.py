# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

try:
    from red_october.exceptions import RedOctoberDecryptException
except ImportError:
    _logger.info('Red October Python library not installed.')


class IrAttachment(models.Model):

    _inherit = 'ir.attachment'

    RED_OCTOBER = 'red_october'

    type = fields.Selection(
        selection_add=[(RED_OCTOBER, 'Red October')],
    )
    red_october_file_id = fields.Many2one(
        string='Red October File',
        comodel_name='red.october.file',
        store=True,
        compute='_compute_red_october_file_id',
        ondelete='cascade',
    )

    @api.multi
    @api.constrains('type')
    def _check_type(self):
        """ It will not allow crypto mutations without a session crypto user.

        Raises:
            ValidationError: If the session does not have a valid
                :type:RedOctoberUser selected.
        """
        if not len(self.filtered(lambda r: r.type == self.RED_OCTOBER)):
            return
        if not self.env['red.october.vault'].get_current_user().exists():
            raise ValidationError(_(
                'Unable to mutate cryptographic fields - Red October has '
                'not been configured for the current user.',
            ))

    @api.multi
    @api.depends('type')
    def _compute_red_october_file_id(self):
        """ It sets the existing Crypto file or creates a new one. """
        for record in self:
            if record.type != self.RED_OCTOBER:
                continue
            if self.env.context.get('__crypt'):
                continue
            ro_file = record.red_october_file_id.upsert_by_attachment(record)
            record.red_october_file_id = ro_file.id
