from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        result = super().session_info()
        if self.env.user._is_internal():
            company_id = self.env.company
            result["issue_auto_send"] = {
                "auto_send": bool(company_id.issue_auto_send_enabled),
                "github": bool(company_id.issue_auto_send_github_url),
                "email": bool(
                    company_id.issue_auto_send_email_enabled
                    and company_id.issue_auto_send_email_to
                ),
                "github_url": company_id.issue_auto_send_github_url or "",
            }
        return result
