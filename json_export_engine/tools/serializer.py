# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

try:
    from odoo.addons.fs_image.fields import FSImageValue
except ImportError:
    FSImageValue = None


class JsonExportSerializer:
    """Generic JSON serializer using jsonifier's record.jsonify()."""

    def __init__(self, parser):
        self.parser = parser

    def serialize(self, record):
        """Serialize a single record into a dict."""
        data = record.jsonify(self.parser, one=True)
        return self._process_values(data)

    def serialize_many(self, records):
        """Serialize a recordset into a list of dicts."""
        result = records.jsonify(self.parser)
        return [self._process_values(item) for item in result]

    def _process_values(self, data):
        """Post-process serialized values to handle binary and special types."""
        for key, value in data.items():
            if isinstance(value, bytes):
                data[key] = base64.b64encode(value).decode("utf-8")
            elif FSImageValue and isinstance(value, FSImageValue):
                data[key] = value.url_path or value.url or value.internal_url
            elif isinstance(value, dict):
                data[key] = self._process_values(value)
            elif isinstance(value, list):
                data[key] = [
                    self._process_values(item) if isinstance(item, dict) else item
                    for item in value
                ]
        return data
