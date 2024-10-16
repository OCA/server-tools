import os

from lxml import etree
from lxml.builder import E

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class XmlExportWizard(models.TransientModel):
    _name = "ir.exports.xml.wizard"
    _description = "Export to XML"

    model_id = fields.Many2one(string="Model", comodel_name="ir.model")
    model_name = fields.Char("Model Name", related="model_id.model", readonly=True)
    domain = fields.Char(default="[]")
    filename = fields.Char(string="File name")
    destination = fields.Char(string="Path to export the file to")
    export_id = fields.Many2one(
        string="Export",
        comodel_name="ir.exports",
        help="If selected, only export fields from the export.",
    )
    module_id = fields.Many2one(
        string="Module",
        comodel_name="ir.module.module",
        help="If selected, exports only fields defined in that module or "
        "its dependencies.",
    )

    @api.multi
    def export_to_xml(self):
        records = self.env[self.model_name].search(safe_eval(self.domain))
        filename = self.filename or "demo_{}.xml".format(records._name)
        destination = self.destination or os.getcwd()
        root = E.odoo()
        xml_records = records.xmlify(export=self.export_id, module=self.module_id)
        for record in xml_records:
            root.append(record)
        content = etree.tostring(root, encoding="unicode", pretty_print=True)
        with open(os.path.join(destination, filename), "w") as output:
            output.write(content)
        return True
