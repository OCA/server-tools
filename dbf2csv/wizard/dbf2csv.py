# -*- coding: utf-8 -*-
# Copyright 2017 INGETIVE (<https://ingetive.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import contextlib
import csv
import base64
import logging
import cStringIO
import os

from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from dbfpy import dbf
except ImportError as err:
    _logger.info(err)


class Conversion(models.TransientModel):
    _name = 'dbftocsv.conversion'
    _description = 'File DBF to convert to CSV'

    data_file = fields.Binary(
        string='DBF file',
        required=True,
        help='Get you DBF file.')
    filename = fields.Char(string='DBF file')

    data_file_csv = fields.Binary(
        string='CSV file',
        readonly=True,
        help='Get you CSV file.')
    filename_csv = fields.Char(string='CSV file')

    def reopen_wizard(self):
        return {
            'type': 'ir.action.act_window',
            'name': 'Conversion',
            'res_model': 'dbftocsv.conversion',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    def process_file(self):
        dbf_buf = cStringIO.StringIO(base64.b64decode(self.data_file))
        csv_buf = cStringIO.StringIO()
        writer = csv.writer(csv_buf)
        with contextlib.closing(dbf.Dbf(dbf_buf)) as in_db:
            writer.writerow([f.name for f in in_db.header.fields])
            for rec in in_db:
                writer.writerow(rec.fieldData)
        self.write({
            'data_file_csv': base64.b64encode(csv_buf.getvalue()),
            'filename_csv': os.path.splitext(self.filename)[0] + '.csv',
        })
        return self.reopen_wizard()

