import logging

from odoo.addons.base.models import ir_module

from .....odoo_patch import OdooPatch

_logger = logging.getLogger(__name__)


class IrModulePatch(OdooPatch):
    target = ir_module.IrModuleModule
    method_names = ("button_immediate_install",)

    def button_immediate_install(self):
        # redirect function call to button_install because post init hooks
        # try to immediate install other modules which fails during reinitialization
        return self.button_install()
