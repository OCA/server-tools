import openerp.tools as tools
import logging

_logger = logging.getLogger(__name__)

# Check if this module is enabled in config
if tools.config.get('gelf_enabled', False):
    try:
        import graypy
    except ImportError:
        _logger.error("Package 'graypy' not installed")
    else:
        _logger.info("GELF_Handler module loading...")

        gelf_host = tools.config['gelf_host']
        gelf_port = int(tools.config['gelf_port'])
        gelf_localname = tools.config.get('gelf_localname')

        kwargs = {}
        if gelf_localname:
            kwargs['localname'] = gelf_localname

        _logger.info("GELF handler config:\n"
                     "\thost: %s\n"
                     "\tport: %s\n"
                     "\tlocalname: %s\n"
                     "", gelf_host, gelf_port, gelf_localname)

        logger = logging.getLogger()

        handler = graypy.GELFHandler(gelf_host, gelf_port, **kwargs)
        logger.addHandler(handler)
