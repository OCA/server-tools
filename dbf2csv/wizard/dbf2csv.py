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

    data_dbf = fields.Binary(
        string='DBF file',
        required=True,
        help='The DBF file that you want to transform.')
    filename_dbf = fields.Char(string='DBF file')

    data_csv = fields.Binary(
        string='CSV file',
        readonly=True,
        help='CSV file transformed and ready to download')
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
        dbf_buf = cStringIO.StringIO(base64.b64decode(self.data_dbf))
        csv_buf = cStringIO.StringIO()
        writer = csv.writer(csv_buf)
        try:
            with contextlib.closing(dbf.Dbf(dbf_buf)) as in_db:
                writer.writerow([f.name for f in in_db.header.fields])
                for rec in in_db:
                    writer.writerow(rec.fieldData)
            self.write({
                'data_csv': base64.b64encode(csv_buf.getvalue()),
                'filename_csv': os.path.splitext(self.filename_dbf)[0] + '.csv',
            })
            return self.reopen_wizard()
        except ValueError:
            _logger.error("Could not convert to CSV", exc_info=True)
            raise UserError(_("Unable to convert to csv"))
