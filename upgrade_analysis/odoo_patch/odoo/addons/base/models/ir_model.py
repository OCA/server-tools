import logging

# ruff: noqa
from odoo import models

from odoo.addons.base.models import ir_model

from ...... import upgrade_log
from .....odoo_patch import OdooPatch

_logger = logging.getLogger(__name__)


class IrModelConstraintPatch(OdooPatch):
    target = ir_model.IrModelConstraint
    method_names = ["_reflect_constraints", "_reflect_table_object"]

    def _reflect_constraints(self, model_names):
        self = self.with_context(_reflect_table_object_result=[])
        self._reflect_constraints._original_method(self, model_names)
        for xml_update_data in self.env.context["_reflect_table_object_result"]:
            xmlid = xml_update_data["xml_id"]
            upgrade_log.log_xml_id(self.env.cr, xmlid.split(".")[0], xmlid)

    def _reflect_table_object(self, model):
        result = self._reflect_table_object._original_method(self, model)
        self.env.context["_reflect_table_object_result"].extend(result)
        return result
