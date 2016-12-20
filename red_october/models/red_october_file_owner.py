# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime

from odoo import api, fields, models


class RedOctoberFileOwner(models.Model):

    _name = 'red.october.file.owner'
    _description ='Red October File Owner'

    vault_id = fields.Many2one(
        string='Vault',
        comodel_name='red.october.vault',
        related='file_id.vault_id',
        readonly=True,
    )
    file_id = fields.Many2one(
        string='File',
        comodel_name='red.october.file',
        required=True,
        ondelete='cascade',
    )
    user_id = fields.Many2one(
        string='User',
        comodel_name='red.october.user',
        domain="[('vault_ids', 'in', vault_id)]",
        required=True,
    )
    name = fields.Char(
        related='user_id.name',
    )
