# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
from contextlib import contextmanager
from unittest.mock import patch

import odoo.tests
from odoo.tests.common import TEST_CURSOR_COOKIE_NAME

from odoo.addons.base_report_paper_muncher.paper_muncher import (
    SERVE_TIMEOUT,
    PaperMuncherInfo,
    PaperMuncherServer,
    paper_muncher,
)


@contextmanager
def release_test_lock(registry):
    """Release the registry test lock while Paper Muncher serves HTTP requests."""
    test_lock = registry.test_lock
    if not test_lock:
        yield
        return
    test_lock.release()
    try:
        yield
    finally:
        test_lock.acquire()


@odoo.tests.tagged("post_install", "-at_install")
class TestPaperMuncherReport(odoo.tests.HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.report = cls.env["ir.actions.report"].create(
            {
                "name": "Test Paper Muncher Report",
                "model": "res.partner",
                "report_name": "base_report_paper_muncher.test_report_partner",
                "report_type": "qweb-pdf",
                "paperformat_id": cls.env.ref("base.paperformat_euro").id,
            }
        )
        cls.env["ir.ui.view"].create(
            {
                "type": "qweb",
                "name": "base_report_paper_muncher.test_report_partner",
                "key": "base_report_paper_muncher.test_report_partner",
                "arch": """
                <t t-name="base_report_paper_muncher.test_report_partner">
                    <t t-call="web.html_container">
                        <t t-foreach="docs" t-as="doc">
                            <div class="article"
                                 t-att-data-oe-model="doc._name"
                                 t-att-data-oe-id="doc.id">
                                <p>Name: <t t-esc="doc.name"/></p>
                            </div>
                        </t>
                    </t>
                </t>
            """,
            }
        )
        cls.partners = cls.env["res.partner"].create(
            [
                {"name": "PM Test Partner 1"},
                {"name": "PM Test Partner 2"},
            ]
        )

    def setUp(self):
        super().setUp()
        if paper_muncher().state != "ok":
            return

        self_setup = self
        old_serve = PaperMuncherServer.serve

        def patched_serve_paper_muncher(
            self_server, documents, *, timeout=SERVE_TIMEOUT
        ):
            test_cookie = f"{TEST_CURSOR_COOKIE_NAME}=paper-muncher"
            if "HTTP_COOKIE" in self_server._wsgi_environ:
                self_server._wsgi_environ["HTTP_COOKIE"] += f", {test_cookie}"
            else:
                self_server._wsgi_environ["HTTP_COOKIE"] = test_cookie

            with (
                patch.object(self_setup, "http_request_key", "paper-muncher"),
                release_test_lock(self_setup.registry),
            ):
                return old_serve(self_server, documents, timeout=timeout)

        self.startPatcher(
            patch.object(
                PaperMuncherServer,
                "serve",
                patched_serve_paper_muncher,
            )
        )

    def _require_paper_muncher_binary(self):
        if paper_muncher().state != "ok":
            self.skipTest("paper-muncher binary not found")

    def _render_pdf(self, partner_ids):
        return (
            self.env["ir.actions.report"]
            .with_context(
                force_report_rendering=True,
            )
            ._render_qweb_pdf(self.report, partner_ids)[0]
        )

    def test_render_single_document(self):
        self._require_paper_muncher_binary()
        pdf = self._render_pdf([self.partners[0].id])
        self.assertTrue(
            pdf.startswith(b"%PDF-"), f"Expected a valid PDF got:\n{pdf[:200]}"
        )

    def test_render_multiple_documents(self):
        self._require_paper_muncher_binary()
        pdf = self._render_pdf(self.partners.ids)
        self.assertTrue(
            pdf.startswith(b"%PDF-"), f"Expected a valid PDF got:\n{pdf[:200]}"
        )


@odoo.tests.tagged("post_install", "-at_install")
class TestPaperMuncherEngine(odoo.tests.TransactionCase):
    def test_resolve_pdf_engine_wkhtmltopdf_forced(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "report.pdf_engine", "wkhtmltopdf"
        )
        resolution = self.env["ir.actions.report"]._resolve_pdf_engine()
        self.assertEqual(resolution.engine, "wkhtmltopdf")
        self.assertFalse(resolution.use_paper_muncher)

    def test_resolve_pdf_engine_auto_with_paper_muncher(self):
        pm_info = PaperMuncherInfo("ok", "/usr/bin/paper-muncher", "0.3.1")
        self.env["ir.config_parameter"].sudo().set_param("report.pdf_engine", "auto")
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.paper_muncher",
            return_value=pm_info,
        ):
            resolution = self.env["ir.actions.report"]._resolve_pdf_engine()
        self.assertEqual(resolution.engine, "auto")
        self.assertTrue(resolution.use_paper_muncher)

    def test_get_wkhtmltopdf_state_with_paper_muncher(self):
        pm_info = PaperMuncherInfo("ok", "/usr/bin/paper-muncher", "0.3.1")
        self.env["ir.config_parameter"].sudo().set_param("report.pdf_engine", "auto")
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.paper_muncher",
            return_value=pm_info,
        ):
            self.assertEqual(
                self.env["ir.actions.report"].get_wkhtmltopdf_state(), "ok"
            )

    def test_fallback_wkhtmltopdf_when_forced(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "report.pdf_engine", "wkhtmltopdf"
        )
        report = self.env["ir.actions.report"]
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.IrActionsReport._run_paper_muncher",
        ) as mock_paper_muncher:
            with patch(
                "odoo.addons.base.models.ir_actions_report.IrActionsReport._run_wkhtmltopdf",
                return_value=b"%PDF-fallback",
            ) as mock_super:
                result = report._run_wkhtmltopdf(["<html><body></body></html>"])
        mock_paper_muncher.assert_not_called()
        mock_super.assert_called_once()
        self.assertEqual(result, b"%PDF-fallback")

    def test_debug_flag_not_enabled_by_default(self):
        report = self.env["ir.actions.report"]
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report._paper_muncher_debug_enabled",
            return_value=False,
        ):
            extra_args = report._build_paper_muncher_extra_args()
        self.assertNotIn("--debug", extra_args)

    def test_debug_flag_enabled_with_env(self):
        report = self.env["ir.actions.report"]
        with patch.dict(os.environ, {"ODOO_PAPER_MUNCHER_DEBUG": "1"}):
            extra_args = report._build_paper_muncher_extra_args()
        self.assertIn("--debug", extra_args)
        self.assertIn("http-client", extra_args)
