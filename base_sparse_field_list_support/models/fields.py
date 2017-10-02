# -*- coding: utf-8 -*-

import json

from odoo import fields

#
# Definition and implementation of serialized fields: override
#


def convert_to_cache(self, value, record, validate=True):
    # cache format: dict / list
    value = value or {}
    return value if isinstance(value, (dict, list)) else json.loads(value)


fields.Serialized.convert_to_cache = convert_to_cache
