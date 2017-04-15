# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ElasticsearchValueChar(models.TransientModel):
    _name = 'elasticsearch.value.char'
    _description = 'ElasticSearch Char Value'

    name = fields.Char()
    field_id = fields.Many2one(
        comodel_name='elsaticsearch.field'
    )
