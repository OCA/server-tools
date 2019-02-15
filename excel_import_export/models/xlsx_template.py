# -*- coding: utf-8 -*-
import os
import base64
from odoo import api, fields, models
from odoo.modules.module import get_module_path
from os.path import join as opj


class XLSXTemplate(models.Model):
    """ Master Data for XLSX Templates
    - Excel Template
    - Import/Export Meta Data (dict text)
    - Default values, etc.
    """
    _name = 'xlsx.template'
    _order = 'name'

    name = fields.Char(
        string='Template Name',
        required=True,
    )
    res_model = fields.Char(
        string='Resource Model',
        readonly=True,
        help="The database object this attachment will be attached to.",
    )
    fname = fields.Char(
        string='File Name',
    )
    gname = fields.Char(
        string='Group Name',
        help="Multiple template of same model, can belong to same group,\n"
        "result in multiple template selection",
    )
    description = fields.Char(
        string='Description',
    )
    instruction = fields.Text(
        string='Instruction',
        help="Instruction on how to import/export "
    )
    datas = fields.Binary(
        string='File Content',
    )
    to_csv = fields.Boolean(
        string='Convert to CSV?',
        default=False,
    )
    csv_delimiter = fields.Char(
        string='CSV Delimiter',
        size=1,
        default=',',
        required=True,
        help="Optional for CSV, default is comma.",
    )
    csv_extension = fields.Char(
        string='CSV File Extension',
        size=5,
        default='csv',
        required=True,
        help="Optional for CSV, default is .csv"
    )
    csv_quote = fields.Boolean(
        string='CSV Quoting',
        default=True,
        help="Optional for CSV, default is full quoting."
    )

    @api.model
    def load_xlsx_template(self, tempalte_ids):
        for template in self.browse(tempalte_ids):
            addon = list(template.get_external_id().values())[0].split('.')[0]
            addon_path = get_module_path(addon)
            file_path = False
            for root, dirs, files in os.walk(addon_path):
                for name in files:
                    if name == template.fname:
                        file_path = os.path.abspath(opj(root, name))
            if file_path:
                template.datas = base64.b64encode(open(file_path, 'rb').read())
        return True
