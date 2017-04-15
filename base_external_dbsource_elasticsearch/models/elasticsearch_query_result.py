# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ElasticsearchQueryResult(models.TransientModel):
    _name = 'elasticsearch.query.result'
    _description = 'ElasticSearch Query Result'

    score = fields.Float()
    document_ids = fields.One2many(
        comodel_name='elasticsearch.document',
    )
    query_id = fields.Many2one(
        comodel_name='elasticsearch.query',
    )
