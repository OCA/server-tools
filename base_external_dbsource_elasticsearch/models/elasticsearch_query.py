# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ElasticsearchQuery(models.TransientModel):
    _name = 'elasticsearch.query'
    _description = 'ElasticSearch Query'

    index_id = fields.Many2one(
        string='Query Indexes',
        comodel_name='ealsticsearch.index'
    )
    query = fields.Binary()
    total = fields.Integer(
        string='Total Matches'
    )
    timed_out = fields.Boolean()
    took = fields.Integer()
    max_score = fields.Float()
    result_ids = fields.One2many(
        comodel_name='elasticsearch.query.result',
        inverse_name='query_id'
    )
