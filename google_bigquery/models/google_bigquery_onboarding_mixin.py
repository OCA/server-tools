from odoo import api, fields, models

ONBOARDING_STEP_STATES = [
    ("not_done", "Not done"),
    ("just_done", "Just done"),
    ("done", "Done"),
]
ONBOARDING_STATES = ONBOARDING_STEP_STATES + [("closed", "Closed")]


class GoogleBigQueryOnboardingMixin(models.AbstractModel):
    _name = "google.bigquery.onboarding.mixin"
    _description = "Google BigQuery Onboarding"

    bigquery_onboarding_state = fields.Selection(
        selection=ONBOARDING_STATES, default="not_done"
    )

    bigquery_onboarding_step_credentials_state = fields.Selection(
        selection=ONBOARDING_STEP_STATES, default="not_done"
    )
    bigquery_onboarding_step_models_state = fields.Selection(
        selection=ONBOARDING_STEP_STATES, default="not_done"
    )

    @api.model
    def _get_bigquery_onboarding_steps(self):
        return [
            "bigquery_onboarding_step_credentials_state",
            "bigquery_onboarding_step_models_state",
        ]

    @api.model
    def action_bigquery_credentials_step(self):
        return self.env.ref("base_setup.action_general_configuration").read()[0]

    @api.model
    def action_bigquery_models_step(self):
        return {"type": "ir.actions.client", "tag": "reload"}

    @api.model
    def action_bigquery_service_account_step(self):
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": "https://console.cloud.google.com/iam-admin/serviceaccounts",
        }

    @api.model
    def action_close_bigquery_onboarding(self):
        self.env.company.bigquery_onboarding_state = "closed"

    def get_bigquery_onboarding_panel_template_name(self):
        self.ensure_one()
        return "google_bigquery.onboarding_panel"

    def get_and_update_bigquery_onboarding_state(self):
        return self.get_and_update_onbarding_state(
            "bigquery_onboarding_state", self._get_bigquery_onboarding_steps()
        )
