import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def uninstall_hook(cr, registry):
    _logger.info("Reverting Patches...")
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.model.fields"].with_context(_force_unlink=True).search(
        [("name", "=", "smart_search")]
    ).unlink()
    _logger.info("Done!")
