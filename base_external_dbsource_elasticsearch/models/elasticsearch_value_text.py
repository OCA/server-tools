# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ElasticsearchValueText(models.TransientModel):
    _name = 'elasticsearch.value.text'
    _description = 'ElasticSearch Text Value'

    name = fields.Text()
    field_id = fields.Many2one(
        comodel_name='elsaticsearch.field'
    )
