# Copyright 2024 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, http
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

REQUIRED_KEYS = ["template_content", "xmlid", "language"]
STATEMENT_TEMPLATE_PUT = """\
WITH t AS (
    SELECT jsonb_object_agg(%(language)s, %(template_content)s) AS value, m.res_id
    FROM ir_model_data m
    WHERE module = %(module)s
    AND name = %(name)s
    GROUP BY m.res_id
)
  UPDATE ir_ui_view m
  SET  arch_db = m.arch_db || t.value
  FROM t
  WHERE t.res_id = m.id
"""


class TemplatePut(http.Controller):
    @http.route(
        "/servertools/template-put",
        type="json",
        auth="user",
        methods=["POST"],
        cors="*",
        csrf=False,
    )
    def put_template(self, **kwargs):
        """Refresh template content for xmlid and language."""
        for key in REQUIRED_KEYS:
            if key not in REQUIRED_KEYS:
                raise UserError(_("Missing key in %(key)s in request") % {"key": key})
        language = kwargs.get("language", "en_US")
        template_content = kwargs.get("template_content")
        xmlid = kwargs.get("xmlid", "portal.portal_share_template")
        xmlid_parts = xmlid.split(".")
        query_parms = {
            "language": language,
            "template_content": template_content,
            "module": xmlid_parts[0],
            "name": xmlid_parts[1],
        }
        database_cursor = request.env.cr
        database_cursor.execute(STATEMENT_TEMPLATE_PUT, query_parms)
        result = {"Template has been updated"}
        _logger.debug(
            "Updated template %s in language %s",
            xmlid,
            language,
        )
        return result
