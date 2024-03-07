# © 2021 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import http
from odoo.http import Response, request

from odoo.addons.web.controllers.main import Home


class MonitoringHome(Home):
    @http.route("/monitoring/<string:token>", type="http", auth="none", csrf="*")
    def monitoring(self, token):
        monitoring = request.env["monitoring"].sudo().search([("token", "=", token)])
        if monitoring:
            result = monitoring.validate()
            return Response(
                json.dumps({"status": monitoring.state, "checks": result}),
                headers={"Content-Type": "application/json"},
            )

        script = request.env["monitoring.script"].sudo().search([("token", "=", token)])
        if script:
            result = script.validate(verbose=True)
            return Response(
                json.dumps(result[0] if result else {"status": "unknown"}),
                headers={"Content-Type": "application/json"},
            )

        return request.not_found()
