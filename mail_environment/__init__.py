# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)

try:
    from . import env_mail
except ImportError:
    _logger.info("ImportError raised while loading module.")
    _logger.debug("ImportError details:", exc_info=True)
