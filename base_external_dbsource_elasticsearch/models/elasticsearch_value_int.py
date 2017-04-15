# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ElasticsearchValueInt(models.TransientModel):
    _name = 'elasticsearch.value.int'
    _description = 'ElasticSearch Int Value'

    name = fields.Integer()
    field_id = fields.Many2one(
        comodel_name='elsaticsearch.field'
    )
