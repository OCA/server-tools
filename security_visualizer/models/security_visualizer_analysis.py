# Copyright 2026 Kobros-Tech Ltd (http://kobros-tech.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json

from odoo import _, api, fields, models


class SecurityVisualizerAnalysis(models.TransientModel):
    """Transient model for storing analysis sessions (temporary)"""

    _name = "security.visualizer.analysis"
    _description = "Security Analysis Session"

    # Analysis parameters
    target_user_id = fields.Many2one("res.users", required=True)
    target_model_id = fields.Many2one("ir.model", required=True)
    target_record_id = fields.Integer("Record ID")
    operation = fields.Selection(
        [
            ("read", "Read"),
            ("write", "Write"),
            ("create", "Create"),
            ("unlink", "Delete"),
        ],
        default="read",
        required=True,
    )

    # Results (computed/stored as JSON)
    analysis_result = fields.Text("Analysis Result (JSON)", readonly=True)
    has_access = fields.Boolean(
        compute="_compute_has_access",
        store=False,
    )
    analysis_summary_html = fields.Html("Analysis Summary", compute="_compute_summary")

    @api.depends("analysis_result")
    def _compute_has_access(self):
        """Extract has_access from JSON result"""
        for record in self:
            if record.analysis_result:
                try:
                    result = json.loads(record.analysis_result)
                    record.has_access = result.get("final_verdict") == "allowed"
                except (ValueError, KeyError):
                    record.has_access = False
            else:
                record.has_access = False

    @api.depends("analysis_result")
    def _compute_summary(self):
        """Generate HTML summary from JSON result"""
        for record in self:
            if not record.analysis_result:
                record.analysis_summary_html = "<p>No analysis performed yet.</p>"
                continue

            try:
                result = json.loads(record.analysis_result)
                html = '<div class="security_analysis_summary">'
                html += f'<h3>{result.get("verdict_explanation", "")}</h3>'

                # Model access section
                if "model_access" in result:
                    ma = result["model_access"]
                    html += "<h4>Model Access:</h4>"
                    html += f'<p>{ma.get("explanation", "")}</p>'

                # Record rules section
                if "record_rules" in result:
                    rr = result["record_rules"]
                    html += "<h4>Record Rules:</h4>"
                    html += f'<p>{rr.get("explanation", "")}</p>'
                    if rr.get("rules"):
                        html += "<ul>"
                        for rule in rr["rules"]:
                            html += ("<li><strong>%s</strong>" ": %s</li>") % (
                                rule["name"],
                                rule["domain"],
                            )
                        html += "</ul>"

                html += "</div>"
                record.analysis_summary_html = html
            except (ValueError, KeyError) as e:
                record.analysis_summary_html = (
                    f"<p>Error parsing analysis: {str(e)}</p>"
                )

    def action_analyze(self):
        """Perform the analysis and store results"""
        self.ensure_one()

        analyzer = self.env["security.analyzer"]

        # Perform comprehensive analysis
        if self.target_record_id:
            result = analyzer.explain_access_decision(
                self.target_model_id.model,
                self.target_user_id.id,
                self.target_record_id,
                self.operation,
            )
        else:
            # Just model and rules analysis, no specific record
            model_access = analyzer.analyze_model_access(
                self.target_model_id.model, self.target_user_id.id, self.operation
            )
            record_rules = analyzer.analyze_record_rules(
                self.target_model_id.model, self.target_user_id.id, self.operation
            )
            result = {
                "model_access": model_access,
                "record_rules": record_rules,
                "final_verdict": "allowed" if model_access["has_access"] else "denied",
                "verdict_explanation": model_access["explanation"],
            }

        # Store as JSON
        self.analysis_result = json.dumps(result, indent=2)

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    @api.model
    def action_open_analyzer(self):
        """Open the analyzer form (called from menu)"""
        return {
            "name": _("Security Analyzer"),
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_operation": "read",
            },
        }

    @api.model
    def rpc_analyze_multicompany_access(self, model_name, user_id, operation="read"):
        """
        RPC method for multi-company access analysis.
        Called from frontend JavaScript.
        """
        analyzer = self.env["security.analyzer"]
        return analyzer.analyze_multicompany_access(model_name, user_id, operation)

    @api.model
    def rpc_get_company_access_matrix(self, user_id, company_ids=None):
        """
        RPC method for company access matrix.
        Called from frontend JavaScript.
        """
        analyzer = self.env["security.analyzer"]
        return analyzer.get_company_access_matrix(user_id, company_ids)

    @api.model
    def rpc_analyze_user_roles(self, user_id):
        """
        RPC method for user role analysis.
        Called from frontend JavaScript.
        """
        analyzer = self.env["security.analyzer"]
        return analyzer.analyze_user_roles(user_id)

    @api.model
    def rpc_analyze_model_access_with_roles(
        self, model_name, user_id, operation="read"
    ):
        """
        RPC method for model access analysis with role information.
        Called from frontend JavaScript.
        """
        analyzer = self.env["security.analyzer"]
        return analyzer.analyze_model_access_with_roles(model_name, user_id, operation)

    @api.model
    def rpc_explain_access_decision_with_roles(
        self, model_name, user_id, record_id=None, operation="read"
    ):
        """
        RPC method for comprehensive access explanation with roles.
        Called from frontend JavaScript.
        """
        analyzer = self.env["security.analyzer"]
        return analyzer.explain_access_decision_with_roles(
            model_name, user_id, record_id, operation
        )

    @api.model
    def rpc_analyze_crud_summary(self, model_name, user_id, record_id=None):
        """
        RPC method for comprehensive CRUD summary with conflict detection.
        Called from frontend JavaScript.

        This returns ALL 4 CRUD operations with conflict detection.
        """
        analyzer = self.env["security.analyzer"]
        return analyzer.analyze_crud_summary(model_name, user_id, record_id)
