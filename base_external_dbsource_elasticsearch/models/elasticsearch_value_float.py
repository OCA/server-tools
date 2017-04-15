# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ElasticsearchValueFloat(models.Model):
    _name = 'elasticsearch.value.float'
    _description = 'ElasticSearch Float Value'

    name = fields.Float()
    field_id = fields.Many2one(
        comodel_name='elsaticsearch.field'
    )
