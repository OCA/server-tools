# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, fields, models
from odoo.http import request
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class RedOctoberFile(models.Model):

    _name = 'red.october.file'
    _description = 'Red October File'
    _inherits = {'ir.attachment': 'attachment_id'}

    attachment_id = fields.Many2one(
        string='Attachment',
        comodel_name='ir.attachment',
        required=True,
        ondelete='cascade',
    )
    owner_ids = fields.One2many(
        string='Owners',
        comodel_name='red.october.file.owner',
        inverse_name='file_id',
        help='These are the delegations required for decryption.',
    )
    vault_id = fields.Many2one(
        string='Vault',
        comodel_name='red.october.vault',
        required=True,
        default=lambda s: s.env['red.october.vault'].get_current_vault(),
    )
    delegation_min = fields.Integer(
        string='Minimum Delegations',
        default=1,
        required=True,
        help='Minimum amount of delegations that are required from file '
             'owners in order to allow encryption.',
    )

    _sql_constraints = [
        ('attachment_id_unique', 'UNIQUE(attachment_id)',
         'This attachment already has an associated Red October file.'),
    ]

    @api.multi
    @api.constrains('owner_ids')
    def _check_owner_ids(self):
        """ It will not allow the same owner twice.

        Raises:
            ValidationError: If the owner is duplicated on the record.
        """
        for record in self:
            if len(record.owner_ids) != len(set(record.owner_ids)):
                raise ValidationError(_(
                    'This user has already been delegated permissions for '
                    'this file.',
                ))

    @api.model
    def default_get(self, fields):
        result = super(RedOctoberFile, self).default_get(fields)
        result['type'] = self.env['ir.attachment'].RED_OCTOBER
        return result

    @api.multi
    def write(self, vals):
        """ It will not allow vault transfers.

        Raises:
            NotImplementedError: If a vault transfer is being attempted.
        """
        if vals.get('vault_id'):
            changed = self.filtered(
                lambda r: r.vault_id.id != vals['vault_id']
            )
            if len(changed):
                raise NotImplementedError(_(
                    'It is currently not possible to move a file between '
                    'vaults.',
                ))
        return super(RedOctoberFile, self).write(vals)

    @api.model_cr_context
    def upsert_by_attachment(self, attachment):
        """ It returns the RedOctoberFile for attachment or makes a new one.

        Args:
            attachment (IrAttachment): Attachment RecordSet singleton
                to search for.
        Returns:
            RedOctoberFile: The Red October RecordSet singleton for the
                attachment.
        """
        record = self.search([('attachment_id', '=', attachment.id)])
        _logger.debug('Upsert attachment found record %s', record)
        if not record:
            record = self.create({
                'attachment_id': attachment.id,
            })
        return record

    @api.model_cr_context
    def decrypt(self, data, vault=None, user=None, password=None,
                *args, **kwargs):
        """ It decrypts the data and returns the result.

        Args:
            data (str): Base64 encoded, encrypted data.
            vault (RedOctoberVault, optional): The RedOctoberVault to use
                for decryption. Omit to use the current session's vault.
            user (RedOctoberUser, optional): The RedOctoberUser to use
                for decryption. Omit to use the current session's user.
            password (str, optional): Password to use for decryption. Omit
                to use the current session's password.
        Raises:
            red_october.exceptions.RedOctoberDecryptException: In the event
                of a decryption failure.
        Returns:
            str: The decrypted string.
        """
        if not data:
            return
        if vault is None:
            vault = self.env['red.october.vault'].get_current_vault()
        if not user:
            user = vault.get_current_user()
        if not password:
            password = request.session.password
        with vault.get_api(user, password) as api:
            response = api.decrypt(data)
            return response['Data']

    @api.model_cr_context
    def encrypt(self, data, vault=None, user=None, password=None,
                owner_ids=None, delegation_min=1, *args, **kwargs):
        """ It encrypts data to the vault.

        Args:
            data (str): Plain text string to encrypt.
            vault (RedOctoberVault, optional): The RedOctoberVault to use
                for decryption. Omit to use the current session's vault.
            user (RedOctoberUser, optional): The RedOctoberUser to use
                for decryption. Omit to use the current session's user.
            password (str, optional): Password to use for decryption. Omit
                to use the current session's password.
            owner_ids (list of int, optional): Red October User Ids that own
                this. 
            delegation_min (int): Minimum number of delegations required
                in order to decrypt.
        Returns:
            str: Encrypted string, encoded in Base64.
        """
        if not data:
            return
        if vault is None:
            vault = self.env['red.october.vault'].get_current_vault()
        if not user:
            user = vault.get_current_user()
        if not password:
            password = request.session.password
        if owner_ids:
            owners = self.env['red.october.user'].browse(owner_ids)
        else:
            owners = []
        with vault.get_api(user, password) as api:
            return api.encrypt(
                owners=[user.name] + [o.name for o in owners],
                minimum=delegation_min,
                data=data,
            )

    @api.model
    def get_for_field(self, model_name, record_id, field_name,
                      recordset=True):
        record = self.env[model_name].browse(record_id)
        field = record._fields[field_name]
        file = field._get_attachments(record)
        return file if recordset else file.read()
