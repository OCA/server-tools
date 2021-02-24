from odoo.tools.convert import xml_import

from .... import upgrade_log
from ...odoo_patch import OdooPatch


class XMLImportPatch(OdooPatch):
    target = xml_import
    method_names = ["_test_xml_id"]

    def _test_xml_id(self, xml_id):
        res = XMLImportPatch._test_xml_id._original_method(self, xml_id)
        upgrade_log.log_xml_id(self.env.cr, self.module, xml_id)
        return res
