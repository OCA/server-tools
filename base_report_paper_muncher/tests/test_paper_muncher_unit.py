# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
import selectors
import subprocess
from unittest.mock import MagicMock, patch

import h11

import odoo.tests
from odoo.exceptions import UserError

from odoo.addons.base_report_paper_muncher.models.ir_actions_report import (
    _extract_div_fragments,
    make_multi_docs_html,
    partition_on_body,
)
from odoo.addons.base_report_paper_muncher.paper_muncher import (
    FALLBACK_BIN_PATH,
    PaperMuncherInfo,
    PaperMuncherServer,
    _remaining_time,
    paper_muncher,
)


@odoo.tests.tagged("post_install", "-at_install")
class TestPaperMuncherHelpers(odoo.tests.TransactionCase):
    def test_partition_on_body_without_body_tag(self):
        html = "<html><head></head></html>"
        self.assertEqual(partition_on_body(html), (html, "", ""))

    def test_partition_on_body_without_closing_tag(self):
        html = "<html><body><p>content</p></html>"
        self.assertEqual(partition_on_body(html), (html, "", ""))

    def test_partition_on_body_with_body(self):
        html = "<html><body><p>content</p></body></html>"
        pre, body, post = partition_on_body(html)
        self.assertTrue(pre.endswith("<body>"))
        self.assertEqual(body, "<p>content</p>")
        self.assertEqual(post, "</body></html>")

    def test_make_multi_docs_html_with_header_footer(self):
        bodies = [
            "<html><body><p>Page 1</p></body></html>",
            "<html><body><p>Page 2</p></body></html>",
        ]
        header = "<html><body><div>H1</div><div>H2</div></body></html>"
        footer = "<html><body><div>F1</div><div>F2</div></body></html>"
        documents = make_multi_docs_html(bodies, header, footer)
        self.assertEqual(len(documents), 2)
        self.assertIn("H1", documents[0])
        self.assertIn("F1", documents[0])
        self.assertIn("Page 1", documents[0])
        self.assertIn("H2", documents[1])
        self.assertIn("F2", documents[1])
        self.assertIn("Page 2", documents[1])

    def test_make_multi_docs_html_reuses_first_header_when_counts_differ(self):
        bodies = [
            "<html><body><p>Page 1</p></body></html>",
            "<html><body><p>Page 2</p></body></html>",
        ]
        header = "<html><body><div>H1</div></body></html>"
        documents = make_multi_docs_html(bodies, header=header)
        self.assertIn("H1", documents[0])
        self.assertIn("H1", documents[1])

    def test_extract_div_fragments_empty(self):
        self.assertEqual(_extract_div_fragments(""), [])

    def test_make_multi_docs_html_reuses_first_footer_when_counts_differ(self):
        bodies = [
            "<html><body><p>Page 1</p></body></html>",
            "<html><body><p>Page 2</p></body></html>",
        ]
        footer = "<html><body><div>F1</div></body></html>"
        documents = make_multi_docs_html(bodies, footer=footer)
        self.assertIn("F1", documents[0])
        self.assertIn("F1", documents[1])


@odoo.tests.tagged("post_install", "-at_install")
class TestPaperMuncherServerHandlers(odoo.tests.TransactionCase):
    def _make_server(self):
        server = PaperMuncherServer(args=["paper-muncher"], os_env={})
        server._process = MagicMock()
        server._process.stdin = MagicMock()
        server._process.stdin.fileno.return_value = 1
        server._conn = h11.Connection(h11.SERVER, max_incomplete_event_size=8192)
        server._documents = [b"<html><body>doc</body></html>"]
        server._pdf = None
        return server

    def test_handle_get_document(self):
        server = self._make_server()

        def fake_write(fd, data):
            return len(data)

        with (
            patch(
                "odoo.addons.base_report_paper_muncher.paper_muncher.os.write",
                side_effect=fake_write,
            ) as mock_write,
            patch(
                "odoo.addons.base_report_paper_muncher.paper_muncher.selectors.DefaultSelector"
            ) as mock_selector_cls,
        ):
            selector = mock_selector_cls.return_value.__enter__.return_value
            selector.select.return_value = [(None, selectors.EVENT_WRITE)]
            server._handle_get_document(b"0")
        self.assertTrue(mock_write.called)

    def test_handle_get_document_default_index(self):
        server = self._make_server()
        with patch.object(PaperMuncherServer, "_send") as mock_send:
            server._handle_get_document(b".")
        self.assertEqual(mock_send.call_count, 3)

    def test_handle_put(self):
        server = self._make_server()
        pdf_body = b"%PDF-1.4 test"
        with patch.object(PaperMuncherServer, "_send") as mock_send:
            server._handle_put(pdf_body)
        self.assertEqual(server._pdf, pdf_body)
        server._process.stdin.close.assert_called_once()
        self.assertEqual(mock_send.call_count, 2)

    def test_process_request_get_document(self):
        server = self._make_server()
        server._request = h11.Request(
            method=b"GET",
            target=b"/paper-muncher/0.html",
            headers=[(b"Host", b"localhost")],
        )
        server._request_body = bytearray()
        with patch.object(PaperMuncherServer, "_handle_get_document") as mock_get:
            server._process_request()
        mock_get.assert_called_once_with(b"0")

    def test_process_request_put_pdf(self):
        server = self._make_server()
        server._request = h11.Request(
            method=b"PUT",
            target=b"/paper-muncher/output.pdf",
            headers=[(b"Host", b"localhost")],
        )
        server._request_body = bytearray(b"%PDF-1.4")
        with patch.object(PaperMuncherServer, "_handle_put") as mock_put:
            server._process_request()
        mock_put.assert_called_once_with(b"%PDF-1.4")

    def test_handle_fallback_websocket_rejected(self):
        server = self._make_server()
        request = h11.Request(
            method=b"GET",
            target=b"/websocket",
            headers=[(b"Host", b"localhost"), (b"Upgrade", b"websocket")],
        )

        def fake_wsgi(environ, start_response):
            start_response("200 OK", [(b"Upgrade", b"websocket")])
            return [b""]

        with patch(
            "odoo.addons.base_report_paper_muncher.paper_muncher.root",
            fake_wsgi,
        ):
            with self.assertRaises(ValueError):
                server._handle_fallback(request, b"")

    def test_handle_fallback_serves_wsgi_response(self):
        server = self._make_server()
        request = h11.Request(
            method=b"GET",
            target=b"/web/assets/test.css",
            headers=[(b"Host", b"localhost")],
        )
        sent_events = []

        def capture_send(self_server, event, *, deadline=None):
            sent_events.append(event)

        def fake_wsgi(environ, start_response):
            start_response("200 OK", [(b"Content-Type", b"text/css")])
            return [b"body"]

        with patch(
            "odoo.addons.base_report_paper_muncher.paper_muncher.root",
            fake_wsgi,
        ):
            with patch.object(
                PaperMuncherServer, "_send", autospec=True, side_effect=capture_send
            ):
                server._handle_fallback(request, b"")
        self.assertTrue(any(isinstance(e, h11.Response) for e in sent_events))
        self.assertTrue(any(isinstance(e, h11.Data) for e in sent_events))
        self.assertTrue(any(isinstance(e, h11.EndOfMessage) for e in sent_events))

    def test_handle_fallback_x_sendfile(self):
        server = self._make_server()
        request = h11.Request(
            method=b"GET",
            target=b"/web/content/1",
            headers=[(b"Host", b"localhost")],
        )
        sent_events = []

        def capture_send(self_server, event, *, deadline=None):
            sent_events.append(event)

        def fake_wsgi(environ, start_response):
            start_response(
                "200 OK",
                [
                    (b"Content-Type", b"application/octet-stream"),
                    (b"X-Sendfile", b"/tmp/test.bin"),
                    (b"Content-Length", b"0"),
                ],
            )
            return []

        with patch(
            "odoo.addons.base_report_paper_muncher.paper_muncher.root",
            fake_wsgi,
        ):
            with patch("builtins.open", create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.side_effect = [
                    b"chunk1",
                    b"",
                ]
                with patch.object(
                    PaperMuncherServer,
                    "_send",
                    autospec=True,
                    side_effect=capture_send,
                ):
                    with patch(
                        "odoo.addons.base_report_paper_muncher.paper_muncher.os.path.getsize",
                        return_value=6,
                    ):
                        server._handle_fallback(request, b"")
        self.assertTrue(any(isinstance(e, h11.Data) for e in sent_events))

    def test_send_writes_to_subprocess_stdin(self):
        server = self._make_server()

        def fake_write(fd, data):
            return len(data)

        with (
            patch(
                "odoo.addons.base_report_paper_muncher.paper_muncher.os.write",
                side_effect=fake_write,
            ) as mock_write,
            patch.object(server._conn, "send", return_value=b"x" * 10),
            patch(
                "odoo.addons.base_report_paper_muncher.paper_muncher.selectors.DefaultSelector"
            ) as mock_selector_cls,
        ):
            selector = mock_selector_cls.return_value.__enter__.return_value
            selector.select.return_value = [(None, selectors.EVENT_WRITE)]
            server._send(MagicMock())
        mock_write.assert_called()
        server._process.stdin.flush.assert_called()

    def test_remaining_time_raises_on_expired_deadline(self):
        with self.assertRaises(TimeoutError):
            _remaining_time(0)

    def test_serve_raises_without_context_manager(self):
        server = PaperMuncherServer(args=["paper-muncher"])
        with self.assertRaises(RuntimeError):
            server.serve(["<html></html>"])


@odoo.tests.tagged("post_install", "-at_install")
class TestPaperMuncherServerLifecycle(odoo.tests.TransactionCase):
    def test_context_manager_starts_and_terminates_process(self):
        mock_process = MagicMock()
        mock_process.poll.return_value = 0
        with patch(
            "odoo.addons.base_report_paper_muncher.paper_muncher.sp.Popen",
            return_value=mock_process,
        ):
            with PaperMuncherServer(args=["paper-muncher"]) as server:
                self.assertIs(server._process, mock_process)
                self.assertIsNotNone(server._conn)
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once_with(1)

    def test_context_manager_kills_on_wait_timeout(self):
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.wait.side_effect = subprocess.TimeoutExpired("paper-muncher", 1)
        with patch(
            "odoo.addons.base_report_paper_muncher.paper_muncher.sp.Popen",
            return_value=mock_process,
        ):
            with PaperMuncherServer(args=["paper-muncher"]) as server:
                self.assertIs(server._process, mock_process)
        mock_process.kill.assert_called_once()

    def test_context_manager_raises_if_process_already_started(self):
        server = PaperMuncherServer(args=["paper-muncher"])
        server._process = MagicMock()
        with self.assertRaises(RuntimeError):
            server.__enter__()


@odoo.tests.tagged("post_install", "-at_install")
class TestPaperMuncherDetection(odoo.tests.TransactionCase):
    def setUp(self):
        super().setUp()
        paper_muncher.cache_clear()

    def tearDown(self):
        paper_muncher.cache_clear()
        super().tearDown()

    def test_paper_muncher_ok_from_path(self):
        with (
            patch(
                "odoo.addons.base_report_paper_muncher.paper_muncher.find_in_path",
                return_value="/usr/bin/paper-muncher",
            ),
            patch(
                "odoo.addons.base_report_paper_muncher.paper_muncher.sp.run",
                return_value=MagicMock(stdout=b"0.3.1"),
            ),
        ):
            info = paper_muncher()
        self.assertEqual(info.state, "ok")
        self.assertEqual(info.bin, "/usr/bin/paper-muncher")
        self.assertEqual(info.version, "0.3.1")

    def test_paper_muncher_ok_from_fallback_path(self):
        with (
            patch(
                "odoo.addons.base_report_paper_muncher.paper_muncher.find_in_path",
                side_effect=OSError("not found"),
            ),
            patch(
                "odoo.addons.base_report_paper_muncher.paper_muncher.os.path.isfile",
                return_value=True,
            ),
            patch(
                "odoo.addons.base_report_paper_muncher.paper_muncher.sp.run",
                return_value=MagicMock(stdout=b"0.3.1"),
            ),
        ):
            info = paper_muncher()
        self.assertEqual(info.state, "ok")
        self.assertEqual(info.bin, FALLBACK_BIN_PATH)

    def test_paper_muncher_install_when_missing(self):
        with (
            patch(
                "odoo.addons.base_report_paper_muncher.paper_muncher.find_in_path",
                side_effect=OSError("not found"),
            ),
            patch(
                "odoo.addons.base_report_paper_muncher.paper_muncher.os.path.isfile",
                return_value=False,
            ),
        ):
            info = paper_muncher()
        self.assertEqual(info.state, "install")


@odoo.tests.tagged("post_install", "-at_install")
class TestPaperMuncherEngineResolution(odoo.tests.TransactionCase):
    def test_resolve_pdf_engine_auto_without_binary(self):
        pm_info = PaperMuncherInfo("install", "", "")
        self.env["ir.config_parameter"].sudo().set_param("report.pdf_engine", "auto")
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.paper_muncher",
            return_value=pm_info,
        ):
            resolution = self.env["ir.actions.report"]._resolve_pdf_engine()
        self.assertEqual(resolution.engine, "auto")
        self.assertFalse(resolution.use_paper_muncher)

    def test_resolve_pdf_engine_paper_muncher_forced_missing_binary(self):
        pm_info = PaperMuncherInfo("install", "", "")
        self.env["ir.config_parameter"].sudo().set_param(
            "report.pdf_engine", "paper-muncher"
        )
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.paper_muncher",
            return_value=pm_info,
        ):
            with self.assertRaises(UserError):
                self.env["ir.actions.report"]._resolve_pdf_engine()

    def test_should_use_paper_muncher(self):
        pm_info = PaperMuncherInfo("ok", "/usr/bin/paper-muncher", "0.3.1")
        self.env["ir.config_parameter"].sudo().set_param(
            "report.pdf_engine", "paper-muncher"
        )
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.paper_muncher",
            return_value=pm_info,
        ):
            self.assertTrue(self.env["ir.actions.report"]._should_use_paper_muncher())

    def test_get_wkhtmltopdf_state_wkhtmltopdf_forced(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "report.pdf_engine", "wkhtmltopdf"
        )
        with patch(
            "odoo.addons.base.models.ir_actions_report.IrActionsReport.get_wkhtmltopdf_state",
            return_value="ok",
        ) as mock_super:
            state = self.env["ir.actions.report"].get_wkhtmltopdf_state()
        mock_super.assert_called_once()
        self.assertEqual(state, "ok")

    def test_get_wkhtmltopdf_state_paper_muncher_forced_missing(self):
        pm_info = PaperMuncherInfo("install", "", "")
        self.env["ir.config_parameter"].sudo().set_param(
            "report.pdf_engine", "paper-muncher"
        )
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.paper_muncher",
            return_value=pm_info,
        ):
            self.assertEqual(
                self.env["ir.actions.report"].get_wkhtmltopdf_state(), "install"
            )

    def test_get_report_log_label_unknown(self):
        label = self.env["ir.actions.report"]._get_report_log_label()
        self.assertEqual(label, "unknown")

    def test_get_report_log_label_invalid_ref(self):
        label = self.env["ir.actions.report"]._get_report_log_label(
            "invalid.report.ref"
        )
        self.assertEqual(label, "invalid.report.ref")

    def test_get_wkhtmltopdf_state_auto_without_binary_falls_back(self):
        pm_info = PaperMuncherInfo("install", "", "")
        self.env["ir.config_parameter"].sudo().set_param("report.pdf_engine", "auto")
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.paper_muncher",
            return_value=pm_info,
        ):
            with patch(
                "odoo.addons.base.models.ir_actions_report.IrActionsReport.get_wkhtmltopdf_state",
                return_value="broken",
            ) as mock_super:
                state = self.env["ir.actions.report"].get_wkhtmltopdf_state()
        mock_super.assert_called_once()
        self.assertEqual(state, "broken")

    def test_get_report_log_label_from_report_sudo(self):
        report = self.env["ir.actions.report"].create(
            {
                "name": "PM Label Report",
                "model": "res.partner",
                "report_type": "qweb-pdf",
                "report_name": "base_report_paper_muncher.test_label_report",
            }
        )
        label = self.env["ir.actions.report"]._get_report_log_label(report_sudo=report)
        self.assertEqual(label, "base_report_paper_muncher.test_label_report")

    def test_resolve_report_sudo_valid_ref(self):
        report = self.env["ir.actions.report"].create(
            {
                "name": "PM Resolve Report",
                "model": "res.partner",
                "report_type": "qweb-pdf",
                "report_name": "base_report_paper_muncher.test_resolve_report",
            }
        )
        resolved = self.env["ir.actions.report"]._resolve_report_sudo(report)
        self.assertEqual(resolved, report)


@odoo.tests.tagged("post_install", "-at_install")
class TestPaperMuncherRun(odoo.tests.TransactionCase):
    def test_run_wkhtmltopdf_delegates_to_paper_muncher(self):
        pm_info = PaperMuncherInfo("ok", "/usr/bin/paper-muncher", "0.3.1")
        report = self.env["ir.actions.report"]
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.paper_muncher",
            return_value=pm_info,
        ):
            with patch(
                "odoo.addons.base_report_paper_muncher.models.ir_actions_report.IrActionsReport._run_paper_muncher",
                return_value=b"%PDF-mock",
            ) as mock_run:
                with patch(
                    "odoo.addons.base.models.ir_actions_report.IrActionsReport._run_wkhtmltopdf",
                ) as mock_super:
                    result = report._run_wkhtmltopdf(["<html><body></body></html>"])
        mock_run.assert_called_once()
        mock_super.assert_not_called()
        self.assertEqual(result, b"%PDF-mock")

    def test_run_wkhtmltopdf_auto_fallback_logs(self):
        pm_info = PaperMuncherInfo("install", "", "")
        report = self.env["ir.actions.report"]
        self.env["ir.config_parameter"].sudo().set_param("report.pdf_engine", "auto")
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.paper_muncher",
            return_value=pm_info,
        ):
            with patch(
                "odoo.addons.base.models.ir_actions_report.IrActionsReport._run_wkhtmltopdf",
                return_value=b"%PDF-fallback",
            ) as mock_super:
                result = report._run_wkhtmltopdf(["<html><body></body></html>"])
        mock_super.assert_called_once()
        self.assertEqual(result, b"%PDF-fallback")

    def test_run_wkhtmltopdf_wkhtmltopdf_forced_logs(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "report.pdf_engine", "wkhtmltopdf"
        )
        report = self.env["ir.actions.report"]
        with patch(
            "odoo.addons.base.models.ir_actions_report.IrActionsReport._run_wkhtmltopdf",
            return_value=b"%PDF-wk",
        ) as mock_super:
            result = report._run_wkhtmltopdf(["<html><body></body></html>"])
        mock_super.assert_called_once()
        self.assertEqual(result, b"%PDF-wk")

    def test_run_paper_muncher_with_request_session(self):
        pm_info = PaperMuncherInfo("ok", "/usr/bin/paper-muncher", "0.3.1")
        report = self.env["ir.actions.report"]
        mock_server = MagicMock()
        mock_server.serve.return_value = b"%PDF-1.4\n"
        mock_server.__enter__ = MagicMock(return_value=mock_server)
        mock_server.__exit__ = MagicMock(return_value=False)
        mock_request = MagicMock()
        mock_request.db = self.env.cr.dbname
        mock_request.session = {"uid": self.env.uid}
        mock_session = MagicMock()
        mock_session.sid = "test-session-id"
        mock_session.uid = self.env.uid
        mock_session_store = MagicMock()
        mock_session_store.new.return_value = mock_session
        captured = {}

        def capture_server_init(*args, **kwargs):
            captured["wsgi_environ"] = kwargs.get("wsgi_environ", {})
            return mock_server

        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.request",
            mock_request,
        ):
            with patch(
                "odoo.addons.base.models.ir_actions_report.IrActionsReport._get_report_url",
                return_value="http://localhost:8069/report/pdf",
            ):
                with patch(
                    "odoo.addons.base_report_paper_muncher.models.ir_actions_report.root.session_store",
                    mock_session_store,
                ):
                    with patch(
                        "odoo.addons.base_report_paper_muncher.models.ir_actions_report.security.compute_session_token",
                        return_value="token",
                    ):
                        with patch(
                            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.PaperMuncherServer",
                            side_effect=capture_server_init,
                        ):
                            pdf = report._run_paper_muncher(
                                ["<html><body></body></html>"],
                                pm_info=pm_info,
                            )
        self.assertEqual(pdf, b"%PDF-1.4\n")
        self.assertIn("HTTP_COOKIE", captured["wsgi_environ"])
        self.assertIn("HTTP_HOST", captured["wsgi_environ"])
        mock_session_store.save.assert_called_once()
        mock_session_store.delete.assert_called_once()

    def test_run_paper_muncher_success(self):
        pm_info = PaperMuncherInfo("ok", "/usr/bin/paper-muncher", "0.3.1")
        report = self.env["ir.actions.report"]
        mock_server = MagicMock()
        mock_server.serve.return_value = b"%PDF-1.4\n"
        mock_server.__enter__ = MagicMock(return_value=mock_server)
        mock_server.__exit__ = MagicMock(return_value=False)
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.PaperMuncherServer",
            return_value=mock_server,
        ):
            pdf = report._run_paper_muncher(
                ["<html><body><p>Test</p></body></html>"],
                pm_info=pm_info,
            )
        self.assertEqual(pdf, b"%PDF-1.4\n")
        mock_server.serve.assert_called_once()

    def test_run_paper_muncher_non_list_bodies(self):
        pm_info = PaperMuncherInfo("ok", "/usr/bin/paper-muncher", "0.3.1")
        report = self.env["ir.actions.report"]
        mock_server = MagicMock()
        mock_server.serve.return_value = b"%PDF-1.4\n"
        mock_server.__enter__ = MagicMock(return_value=mock_server)
        mock_server.__exit__ = MagicMock(return_value=False)
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.PaperMuncherServer",
            return_value=mock_server,
        ):
            pdf = report._run_paper_muncher(
                ("<html><body></body></html>",),
                pm_info=pm_info,
            )
        self.assertEqual(pdf, b"%PDF-1.4\n")
        mock_server.serve.assert_called_once()

    def test_run_paper_muncher_failure_raises_user_error(self):
        pm_info = PaperMuncherInfo("ok", "/usr/bin/paper-muncher", "0.3.1")
        report = self.env["ir.actions.report"]
        mock_server = MagicMock()
        mock_server.serve.side_effect = subprocess.CalledProcessError(
            1, "paper-muncher"
        )
        mock_server.__enter__ = MagicMock(return_value=mock_server)
        mock_server.__exit__ = MagicMock(return_value=False)
        with patch(
            "odoo.addons.base_report_paper_muncher.models.ir_actions_report.PaperMuncherServer",
            return_value=mock_server,
        ):
            with self.assertRaises(UserError):
                report._run_paper_muncher(
                    ["<html><body></body></html>"],
                    pm_info=pm_info,
                )


@odoo.tests.tagged("post_install", "-at_install")
class TestPaperMuncherExtraArgs(odoo.tests.TransactionCase):
    def test_build_extra_args_landscape(self):
        report = self.env["ir.actions.report"]
        extra_args = report._build_paper_muncher_extra_args(landscape=True)
        self.assertIn("--orientation", extra_args)
        self.assertIn("landscape", extra_args)

    def test_build_extra_args_custom_paperformat(self):
        paperformat = self.env["report.paperformat"].create(
            {
                "name": "PM Custom Format",
                "format": "custom",
                "orientation": "Portrait",
                "page_width": 200,
                "page_height": 300,
            }
        )
        report = self.env["ir.actions.report"]
        extra_args = report._build_paper_muncher_extra_args(paperformat=paperformat)
        self.assertIn("--width", extra_args)
        self.assertIn("200mm", extra_args)
        self.assertIn("--height", extra_args)
        self.assertIn("300mm", extra_args)

    def test_build_extra_args_standard_paperformat(self):
        paperformat = self.env.ref("base.paperformat_euro")
        report = self.env["ir.actions.report"]
        extra_args = report._build_paper_muncher_extra_args(paperformat=paperformat)
        self.assertIn("--paper", extra_args)
        self.assertIn(paperformat.format, extra_args)

    def test_build_extra_args_specific_paperformat_args(self):
        report = self.env["ir.actions.report"]
        extra_args = report._build_paper_muncher_extra_args(
            specific_paperformat_args={
                "data-report-landscape": True,
                "data-report-dpi": 96,
            }
        )
        self.assertIn("--orientation", extra_args)
        self.assertIn("landscape", extra_args)
        self.assertIn("96dpi", extra_args)

    def test_build_extra_args_feature_flag(self):
        report = self.env["ir.actions.report"]
        with patch.dict(os.environ, {"ODOO_PAPER_MUNCHER_FEATURE": "1"}):
            extra_args = report._build_paper_muncher_extra_args()
        self.assertIn("--feature", extra_args)
        self.assertIn("*=on", extra_args)

    def test_build_extra_args_portrait_orientation(self):
        paperformat = self.env.ref("base.paperformat_euro")
        report = self.env["ir.actions.report"]
        extra_args = report._build_paper_muncher_extra_args(paperformat=paperformat)
        self.assertIn("--orientation", extra_args)
        self.assertIn("portrait", extra_args)
