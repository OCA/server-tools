# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Jairo Llopis
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import logging
from psycopg2 import IntegrityError
from openerp.addons.module_auto_update.models.module_deprecated import \
    PARAM_DEPRECATED

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Autoenable deprecated behavior."""
    try:
        cr.execute(
            "INSERT INTO ir_config_parameter (key, value) VALUES (%s, '1')",
            (PARAM_DEPRECATED,)
        )
        _logger.warn("Deprecated features have been autoenabled, see "
                     "addon's README to know how to upgrade to the new "
                     "supported autoupdate mechanism.")
    except IntegrityError:
        _logger.info("Deprecated features setting exists, not autoenabling")
