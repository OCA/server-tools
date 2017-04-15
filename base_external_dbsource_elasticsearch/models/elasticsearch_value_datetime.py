# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ElasticsearchValueDatetime(models.TransientModel):
    _name = 'elasticsearch.value.datetime'
    _description = 'ElasticSearch Datetime Value'

    name = fields.DateTime()
    field_id = fields.Many2one(
        comodel_name='elsaticsearch.field'
    )
