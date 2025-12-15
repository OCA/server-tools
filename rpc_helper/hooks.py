# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo.service import model

from .patch import protected__execute_cr

_logger = logging.getLogger(__name__)


def patch__model_execute_cr():
    """Patch rpc model handler."""
    protected__execute_cr._orig__execute_cr = model.execute_cr
    model.execute_cr = protected__execute_cr
    _logger.info("PATCHED odoo.service.model.execute")


def post_load_hook():
    patch__model_execute_cr()
