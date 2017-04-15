# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ElasticsearchIndex(models.Model):
    _name = 'elasticsearch.index'
    _description = 'ElasticSearch Index'
