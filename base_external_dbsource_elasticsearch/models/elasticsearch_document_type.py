# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ElasticsearchDocumentType(models.TransientModel):
    _name = 'elasticsearch.document.type'
    _description = 'ElasticSearch Document Type'

    name = fields.Char()
    index_id = fields.Many2one(
        comodel_name='elasticsearch.index'
    )
    document_ids = fields.One2many(
        comodel_name='elasticsearch.document',
        inverse_name='type_id'
    )
