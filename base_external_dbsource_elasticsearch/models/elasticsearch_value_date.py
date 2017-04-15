# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ElasticsearchValueDate(models.TransientModel):
    _name = 'elasticsearch.value.date'
    _description = 'ElasticSearch Date Value'

    name = fields.Date()
    field_id = fields.Many2one(
        comodel_name='elsaticsearch.field'
    )
