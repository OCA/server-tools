# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ElasticsearchField(models.TransientModel):
    _name = 'elasticsearch.field'
    _description = 'ElasticSearch Field'

    document_id = fields.Many2one(
        comodel_name='elasticsearch.document',
    )
    value_id = fields.One2many(
        # Fix
    )
