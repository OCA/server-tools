# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import psycopg2

from odoo import fields

from odoo.tools import human_size


_logger = logging.getLogger(__name__)


class RedOctober(fields.Field):

    type = 'red_october'
    column_type = None

    def convert_to_column(self, value, record):
        return

    def convert_to_cache(self, value, record, validate=True):
        if isinstance(value, buffer):
            return str(value)
        return value

    def read(self, records):
        # values are stored in attachments, retrieve them
        attachments = self._get_attachments(records).with_context(
            bin_size=False,
        )
        data = {att.res_id: att.datas for att in attachments}
        _logger.debug(data)
        for record in records:
            record._cache[self.name] = data.get(record.id, False)

    def write(self, records, value):
        # retrieve the attachments that stores the value, and adapt them
        attachments = self._get_attachments(records)
        _logger.debug('Writing %s with %s', attachments, value)
        with records.env.norecompute():
            if value:
                # update the existing attachments
                attachments.write({
                    'datas': value,
                })
                missing_attachments = (
                    records - records.browse(attachments.mapped('res_id'))
                )
                for record in missing_attachments:
                    self._create_attachment(record, value)
            else:
                attachments.unlink()

    def _create_attachment(self, record, value):
        record.env['red.october.file'].create({
            'name': self.name,
            'res_model': record._name,
            'res_field': self.name,
            'res_id': record.id,
            'datas': value,
        })

    def _get_attachments(self, records):
        domain = [
            ('res_model', '=', records._name),
            ('res_field', '=', self.name),
            ('res_id', 'in', records.ids),
        ]
        return records.env['red.october.file'].sudo().search(domain)
