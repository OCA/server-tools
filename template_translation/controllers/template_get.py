# Copyright 2024 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


STATEMENT_TEMPLATE_GET = """\
SELECT vw.arch_db::jsonb->%(language)s
  FROM ir_ui_view vw
  JOIN ir_model_data md ON vw.id = md.res_id
    AND md.model = 'ir.ui.view'
  WHERE md.module = %(module)s
    AND md.name = %(name)s
"""


class TemplateGet(http.Controller):
    @http.route(
        "/servertools/template-get",
        type="json",
        auth="user",
        methods=["GET"],
        cors="*",
        csrf=False,
    )
    def get_template(self, **kwargs):
        """Get template contents from xmlid and language."""
        # Create exactly what is shown in #8264 attachment
        xmlid = kwargs.get("xmlid", "portal.portal_share_template")
        language = kwargs.get("language", "en_US")
        xmlid_parts = xmlid.split(".")
        query_parms = {
            "language": language,
            "module": xmlid_parts[0],
            "name": xmlid_parts[1],
        }
        database_cursor = request.env.cr
        database_cursor.execute(STATEMENT_TEMPLATE_GET, query_parms)
        template_content = database_cursor.fetchone()[0]
        result = {
            "template_content": template_content,
        }
        _logger.debug(
            "Retrieved template %s in language %s",
            xmlid,
            language,
        )
        return result
