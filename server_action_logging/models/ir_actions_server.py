# © 2024 Camptocamp (https://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

DEFAULT_LOG_CONFIGURATION = [
    "odoo.http.rpc.request:INFO",
    "odoo.http.rpc.response:INFO",
    ":INFO",
]


class IrActionsServer(models.Model):

    _inherit = "ir.actions.server"

    enable_sql_debug = fields.Boolean(
        string="Enable SQL Debug", help="Enable SQL Debug for this action", default=True
    )

    def run(self):
        log_handlers = DEFAULT_LOG_CONFIGURATION
        res = False
        for action in self:
            if action.enable_sql_debug:
                self._update_logger_level(log_handlers)
            start_time = fields.Datetime.now()
            _logger.info(
                "Running action with id %s and name %s",
                action.id,
                action.name,
            )
            try:
                res = super(IrActionsServer, action).run()
            finally:
                _logger.info(
                    "Action with id %s and name %s took %s seconds",
                    action.id,
                    action.name,
                    fields.Datetime.now() - start_time,
                )
                self._update_logger_level(log_handlers, True)
        return res or False

    def _update_logger_level(self, log_handlers, reset=False):
        # check odoo/src/odoo/netsvc.py:234
        debug_sql_handler = "odoo.sql_db:DEBUG"
        if debug_sql_handler in log_handlers:
            # There is nothing to do, the entry is already inside
            return False
        if reset:
            loggername, level = debug_sql_handler.strip().split(":")
            logger = logging.getLogger(loggername)
            logger.setLevel("NOTSET")
            return True
        # # We add if necessary new logger entry
        logging_configurations = log_handlers + [debug_sql_handler]
        for logconfig_item in logging_configurations:
            loggername, level = logconfig_item.strip().split(":")
            level = getattr(logging, level, logging.INFO)
            logger = logging.getLogger(loggername)
            logger.setLevel(level)
        return True
