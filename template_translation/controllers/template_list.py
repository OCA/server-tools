# Copyright 2024 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


STATEMENT_TEMPLATE_LIST = """\
SELECT name
  FROM ir_model_data md
  WHERE md.model = 'ir.ui.view'
  AND md.module = %(module)s
"""


class TemplateList(http.Controller):
    @http.route(
        "/servertools/template-list",
        type="json",
        auth="user",
        methods=["GET"],
        cors="*",
        csrf=False,
    )
    def list_template(self, **kwargs):
        """List template names in module."""
        module = kwargs.get("module", "base")
        query_parms = {
            "module": module,
        }
        database_cursor = request.env.cr
        database_cursor.execute(STATEMENT_TEMPLATE_LIST, query_parms)
        templates = database_cursor.fetchall()
        result = {
            "template_list": [template[0] for template in templates],
        }
        _logger.debug(
            "Retrieved %d template xmlid's",
            len(templates),
        )
        return result
