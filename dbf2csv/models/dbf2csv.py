# -*- coding: utf-8 -*-
# Copyright 2017 INGETIVE (<https://ingetive.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import tempfile
import csv
import base64
import logging

from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from dbfpy import dbf
except ImportError as err:
    _logger.debug(err)


class Conversion(models.Model):
    _name = 'dbftocsv.conversion'
    _description = 'File DBF to convert to CSV'

    name = fields.Char(string='Description', required=True)

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

    def process_file(self):
        try:
            with tempfile.NamedTemporaryFile(mode='w+') as tmp_dbf_file:
                tmp_dbf_file.write(base64.decodestring(self.data_file))
                with tempfile.NamedTemporaryFile(mode='w+') as tmp_csv_file:
                    in_db = dbf.Dbf(tmp_dbf_file)
                    out_csv = csv.writer(tmp_csv_file)
                    names = []
                    for field in in_db.header.fields:
                        names.append(field.name)
                    out_csv.writerow(names)
                    for rec in in_db:
                        out_csv.writerow(rec.fieldData)
                    in_db.close()
                    tmp_csv_file.seek(0)
                    file_csv_content = tmp_csv_file.read()
                    self.data_file_csv = base64.encodestring(file_csv_content)
                    self.filename_csv = self.filename.replace('.dbf', '.csv')
                    tmp_csv_file.close()
                tmp_dbf_file.close()
        except (IOError, OSError):
            raise UserError(_("Unable to save csv file"))
        except ValueError:
            raise UserError(_("Unable to convert to csv"))
