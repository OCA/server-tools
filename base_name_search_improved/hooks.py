import logging

_logger = logging.getLogger(__name__)


def uninstall_hook(env):
    _logger.info("Reverting Patches...")
    env["ir.model.fields"].with_context(_force_unlink=True).search(
        [("name", "=", "smart_search")]
    ).unlink()
    _logger.info("Done!")
