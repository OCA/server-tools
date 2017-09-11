# -*- coding: utf-8 -*-
# Copyright 2017 INGETIVE (<https://ingetive.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import csv
import base64
import logging
from odoo import models, fields, api

try:
    from dbfpy import dbf
except ImportError:
    dbfpy = None

logger = logging.getLogger(__name__)


class FileDBF(models.TransientModel):
    _name = 'dbftocsv.filedbf'
    _description = 'File DBF to convert to CSV'

    data_file = fields.Binary(
        string='DBF file',
        required=True,
        help='Get you DBF file.')
    filename = fields.Char(string='DBF file name')

    @api.multi
    def proccess_file(self):
        # Process the DBF file chosen in the wizard,
        # create and download CSV file.
        self.ensure_one()
        # Create DBF file in TMP
        fp = open('/tmp/' + self.filename, 'w+')
        fp.write(base64.decodestring(self.data_file))
        fp.close()

        with open('/tmp/' + self.filename.replace('dbf', 'csv'),
                  'w+') as csvfile:
            in_db = dbf.Dbf('/tmp/' + self.filename)
            out_csv = csv.writer(csvfile)
            names = []
            for field in in_db.header.fields:
                names.append(field.name)
            out_csv.writerow(names)
            for rec in in_db:
                out_csv.writerow(rec.fieldData)
            in_db.close()

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?filename=%s'
            % (self.filename.replace('dbf', 'csv')),
            'target': 'new',
        }
