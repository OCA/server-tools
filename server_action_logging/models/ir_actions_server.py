# © 2024 Camptocamp (https://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

ODOO_TOOL_CONFIG_HANDLER_NAME = "log_handler"
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
        LOG_HANDLERS = DEFAULT_LOG_CONFIGURATION
        for action in self:
            if action.enable_sql_debug:
                self._update_logger_level(LOG_HANDLERS)
            start_time = fields.Datetime.now()
            _logger.info(
                "Running action with id %s and name %s",
                action.id,
                action.name,
            )
            super(IrActionsServer, action).run()
            _logger.info(
                "Action with id %s and name %s took %s seconds",
                action.id,
                action.name,
                fields.Datetime.now() - start_time,
            )
        self._update_logger_level(LOG_HANDLERS, True)
        return

    def _update_logger_level(self, log_handlers, reset=False):
        # check odoo/src/odoo/netsvc.py:260
        DEBUG_SQL = "odoo.sql_db:DEBUG"
        if DEBUG_SQL in log_handlers:
            # There is nothing to do, the entry is already inside
            return False
        if reset:
            loggername, level = DEBUG_SQL.strip().split(":")
            logger = logging.getLogger(loggername)
            logger.setLevel("NOTSET")
            return True
        # # We add if necessary new logger entry
        logging_configurations = log_handlers + [DEBUG_SQL]
        for logconfig_item in logging_configurations:
            loggername, level = logconfig_item.strip().split(":")
            level = getattr(logging, level, logging.INFO)
            logger = logging.getLogger(loggername)
            logger.setLevel(level)
        return True
