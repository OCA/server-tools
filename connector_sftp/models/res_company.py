# -*- coding: utf-8 -*-
# © 2016-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    sftp_connector_ids = fields.One2many(
        string='SFTP Connectors',
        comodel_name='connector.sftp',
        inverse_name='company_id',
    )
