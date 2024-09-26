# Copyright 2024 Camptocamp (https://www.camptocamp.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    enable_sql_debug = fields.Boolean(
        string="Enable SQL Debug",
        help="Enable SQL Debug for this action",
        default=False,  # Avoid too much log pollution
    )

    def run(self):
        if self.env.context.get("server_action_run_with_logs"):  # Avoid recursion
            return super().run()

        actions = self.with_context(server_action_run_with_logs=True)
        odoo_sql_db_logger = logging.getLogger("odoo.sql_db")
        odoo_sql_db_logger_level = odoo_sql_db_logger.level
        odoo_sql_db_logger_has_debug = odoo_sql_db_logger.isEnabledFor(logging.DEBUG)
        res = False
        for act in actions:
            force_sql_debug = not odoo_sql_db_logger_has_debug and act.enable_sql_debug
            if force_sql_debug:
                odoo_sql_db_logger.setLevel(logging.DEBUG)
            subject = f"Action {act.display_name} ({act})"
            _logger.info(f"{subject} started")
            start = fields.Datetime.now()
            res = act.run()
            delta = (fields.Datetime.now() - start).total_seconds()
            _logger.info(f"{subject} completed in {delta:.3f} seconds")
            if force_sql_debug:
                odoo_sql_db_logger.setLevel(odoo_sql_db_logger_level)
        return res or False
