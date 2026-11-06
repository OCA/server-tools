# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
import logging
from collections import defaultdict

from odoo import api, models

_logger = logging.getLogger(__name__)


class AuditlogLog(models.Model):
    _inherit = "auditlog.log"

    @api.model_create_multi
    def create(self, vals_list):
        """Handle auditlog output to STDOUT, rather than creating a record."""
        if not self.env.context.get("auditlog_use_stdout"):
            return super().create(vals_list)

        self.log_to_stdout(vals_list)
        return super().create([])

    def log_to_stdout(self, vals_list):
        """Output the values to a logger,
        as a JSON value containing all the fields in vals_list.

        Optionally, this JSON value can be defined using a system parameter
        'auditlog.stdout_log_format_json', to contain a comma-separated
        list of keys to use and the format specifiers to fill them from vals,
        f.e.:
        '{{"user": "{user_id}", "model": "{model_model}", "id": "{res_id}"}}'
        """
        log_format = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "auditlog.stdout_log_format_json",
            )
        )
        for vals in vals_list:
            if vals.get("model_id"):
                model = self.env["ir.model"].sudo().browse(vals["model_id"])
                vals.update({"model_name": model.name, "model_model": model.model})
            log_output = json.dumps(vals)
            try:
                if log_format:
                    vals_to_use = defaultdict(lambda: "null", vals)
                    log_output = log_format.format_map(vals_to_use)
                    json.loads(log_output)
                _logger.info(log_output)
            except Exception as e:
                _logger.info(json.dumps(vals))
                _logger.error("auditlogging to standard output failed: %s", str(e))
