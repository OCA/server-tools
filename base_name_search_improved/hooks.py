import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


def uninstall_hook(cr, registry):
    _logger.info("Reverting Patches...")
    models.BaseModel._revert_method("fields_view_get")
    _logger.info("Done!")
