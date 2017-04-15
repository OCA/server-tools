# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ElasticsearchDocumentType(models.TransientModel):
    _name = 'elasticsearch.document'
    _description = 'ElasticSearch Document'

    type_id = fields.Many2one(
        string='Document Type',
        comodel_name='elasticsearch.document.type',
    )
    field_ids = fields.One2many(
        string='Document Fields',
        comodel_name='elasticsearch.field',
    )
    score = fields.Integer(
        string='Document Score',
    )
    query_result_id = fields.Many2one(
        string='Document Query Result',
        comodel_name='elasticsearch.query.result'
    )
