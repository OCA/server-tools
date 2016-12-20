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
        inverse='_inverse_red_october_file_id',
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

    @api.multi
    def _inverse_red_october_file_id(self):
        pass

    @api.multi
    @api.depends('store_fname', 'db_datas')
    def _compute_datas(self):
        """ It decrypts the data before showing client. """
        for attachment in self:
            super(IrAttachment, attachment)._compute_datas()
            if all((attachment.type == self.RED_OCTOBER,
                    not self.env.context.get('bin_size'))):
                try:
                    _logger.debug('Decrypting Red October file %s', attachment.datas)
                    decrypted = attachment.red_october_file_id.decrypt(
                        attachment.datas,
                    )
                    _logger.debug('Decrypted to %r', decrypted)
                    attachment.datas = decrypted.decode('base64')
                except RedOctoberDecryptException as e:
                    raise UserError(_(
                        _('A decryption error has occurred:\n%s') % (
                            e.message,
                        )
                    ))

    @api.multi
    def _inverse_datas(self):
        """ It encrypts the data before saving. """
        location = self._storage()
        for attachment in self:
            if attachment.type == self.RED_OCTOBER:

                value = attachment.datas
                _logger.debug('Encrypting Red October file %s', value)

                encrypted = attachment.red_october_file_id.encrypt(value)
                _logger.debug('Encrypted to %s', encrypted)

                bin_data = value and value.decode('base64') or ''
                vals = {
                    'file_size': len(encrypted),
                    'checksum': self._compute_checksum(encrypted),
                    'index_content': self._index(
                        # @TODO: See how ``bin_data`` is used; exposing data.
                        bin_data,
                        attachment.datas_fname,
                        attachment.mimetype,
                    ),
                    'store_fname': False,
                    'db_datas': encrypted,
                }
                if value and location != 'db':
                    # save it to the filestore
                    vals['store_fname'] = self._file_write(encrypted, vals['checksum'])
                    vals['db_datas'] = False

                # take current location in filestore to possibly garbage-collect it
                fname = attachment.store_fname
                # write as superuser, as user probably does not have write access
                attachment = attachment.sudo().with_context(__crypt=True)
                super(IrAttachment, attachment).write(vals)
                if fname:
                    self._file_delete(fname)
            else:
                super(IrAttachment, attachment)._inverse_datas()

    # @api.model
    # def _file_read(self, fname, bin_size=False):
    #     res = super(IrAttachment, self)._file_read(fname, bin_size)
    #     _logger.debug('Decrypting Red October file %s' % res)
    #     decrypted = self.red_october_file_id.decrypt(res)
    #     _logger.debug('Decrypted to %s', decrypted)
    #     return decrypted
    #
    # @api.model
    # def _file_write(self, value, checksum):
    #     res = super(IrAttachment, self)._file_write(value, checksum)
    #     _logger.debug('Decrypting Red October file %s' % res)
    #     encrypted = self.env[''.encrypt(res)
    #     _logger.debug('Encrypted to %s', encrypted)
    #     return encrypted
