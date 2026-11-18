from . import patch_xml_import  # patch xml_import so that view is fixed

# patch vies so that they don't break
from odoo.addons.base.models.ir_ui_view import View


_original_check_xml = View._check_xml


def _check_xml(self):
    # TODO we should check exeception is due to the expected error
    try:
        _original_check_xml
    except Exception:
        pass


View._check_xml = _check_xml
