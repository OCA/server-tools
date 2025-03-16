import logging

_logger = logging.getLogger(__name__)


def uninstall_hook(env):
    _logger.info("Reverting Patches...")
    fields_to_unlink = (
        env["ir.model.fields"]
        .with_context(_force_unlink=True)
        .search([("name", "=", "smart_search")])
    )
    if fields_to_unlink:
        fields_to_unlink.unlink()
    _logger.info("Done!")
