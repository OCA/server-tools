from odoo import http
from odoo.http import request


class OnboardingController(http.Controller):
    @http.route("/google_bigquery/onboarding_panel", auth="user", type="json")
    def onboarding_panel(self):
        company = request.env.company
        if company.bigquery_onboarding_state == "closed":
            return {}

        template_name = company.get_bigquery_onboarding_panel_template_name()
        return {
            "html": request.env.ref(template_name)._render(
                {
                    "company": company,
                    "state": company.get_and_update_bigquery_onboarding_state(),
                }
            )
        }
