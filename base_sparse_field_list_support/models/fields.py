import json

from odoo.addons.base_sparse_field.models import fields

#
# Definition and implementation of serialized fields: override
#


def convert_to_cache(self, value, record, validate=True):
    # cache format: dict / list
    if value is False or value is None:
        value = {}
    return json.dumps(value) if isinstance(value, dict | list) else (value or None)


fields.Serialized.convert_to_cache = convert_to_cache
