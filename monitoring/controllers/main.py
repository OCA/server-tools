# © 2021 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import Response, request

from odoo.addons.web.controllers.main import Home


class MonitoringHome(Home):
    @http.route("/monitoring/<string:token>", type="http", auth="none", csrf="*")
    def monitoring(self, token):
        monitoring = request.env["monitoring"].sudo().search([("token", "=", token)])
        if monitoring:
            return Response(
                monitoring.validate_and_format(),
                headers=monitoring.response_headers(),
            )

        script = request.env["monitoring.script"].sudo().search([("token", "=", token)])
        if script:
            return Response(
                script.validate_and_format(verbose=True),
                headers=script.response_headers(),
            )

        return request.not_found()
