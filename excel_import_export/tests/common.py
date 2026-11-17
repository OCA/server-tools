# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import base64
from io import BytesIO

import openpyxl

from odoo.addons.base.tests.common import BaseCommon


class TestExcelImportExportCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        out = BytesIO()
        wb.save(out)
        out.seek(0)
        cls.dummy_xlsx_b64 = base64.b64encode(out.read())
        cls.partner = cls.env["res.partner"].create({"name": "Test OCA Partner"})
        cls.template = cls.env["xlsx.template"].create(
            {
                "name": "Test Partner Template",
                "res_model": "res.partner",
                "fname": "test_partner.xlsx",
                "datas": cls.dummy_xlsx_b64,
                "input_instruction": "{'__EXPORT__': {'Sheet1': {'_HEAD_': {'A1': 'name','B1': 'phone'}}},'__IMPORT__': {'Sheet1': {'_HEAD_': {'A1': 'name'}}}}",  # noqa: E501
                "to_csv": False,
                "use_report_wizard": False,
            }
        )
