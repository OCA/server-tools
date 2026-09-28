# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os
import re
import subprocess
from collections.abc import Sequence
from contextlib import ExitStack
from typing import NamedTuple
from urllib.parse import urlsplit

import lxml.html

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.http import request, root
from odoo.service import security

from ..paper_muncher import PaperMuncherInfo, PaperMuncherServer, paper_muncher

_logger = logging.getLogger(__name__)

_BODY_TAG_RE = re.compile(r"<body[^>]*>", re.IGNORECASE)


class PdfEngineResolution(NamedTuple):
    engine: str
    use_paper_muncher: bool
    pm_info: PaperMuncherInfo


def _extract_div_fragments(body_content: str) -> list[str]:
    """Extract top-level div fragments from HTML body content."""
    if not body_content:
        return []
    wrapper = lxml.html.fromstring(f"<div>{body_content}</div>")
    return [
        lxml.html.tostring(div, encoding="unicode") for div in wrapper.findall("./div")
    ]


def partition_on_body(html: str) -> tuple[str, str, str]:
    """Split HTML into pre-body, body content, and post-body."""
    match = _BODY_TAG_RE.search(html)
    if not match:
        return html, "", ""
    pre_body = html[: match.end()]
    rest = html[match.end() :]
    body, sep, post_body = rest.rpartition("</body>")
    if not sep:
        return html, "", ""
    return pre_body, body, sep + post_body


def make_multi_docs_html(
    bodies: Sequence[str], header: str = "", footer: str = ""
) -> list[str]:
    """Inject per-page header/footer fragments into each body HTML document."""
    footer_body = partition_on_body(footer)[1]
    footers = _extract_div_fragments(footer_body)

    header_body = partition_on_body(header)[1]
    headers = _extract_div_fragments(header_body)

    is_same_length_header = len(headers) == len(bodies)
    if headers and not is_same_length_header:
        _logger.warning(
            "Header fragments count (%d) does not match body count (%d); "
            "reusing the first header fragment where needed.",
            len(headers),
            len(bodies),
        )

    is_same_length_footer = len(footers) == len(bodies)
    if footers and not is_same_length_footer:
        _logger.warning(
            "Footer fragments count (%d) does not match body count (%d); "
            "reusing the first footer fragment where needed.",
            len(footers),
            len(bodies),
        )

    documents = []
    for i, body in enumerate(bodies):
        pre_body, body_content, post_body = partition_on_body(body)
        header_fragment = (
            headers[i] if is_same_length_header else (headers[0] if headers else "")
        )
        footer_fragment = (
            footers[i] if is_same_length_footer else (footers[0] if footers else "")
        )
        documents.append(
            f"{pre_body}{header_fragment}{body_content}{footer_fragment}{post_body}\n"
        )

    return documents


def _paper_muncher_debug_enabled():
    return os.getenv("ODOO_PAPER_MUNCHER_DEBUG") == "1" or _logger.isEnabledFor(
        logging.DEBUG
    )


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _get_pdf_engine_config(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("report.pdf_engine", "auto")
        )

    @api.model
    def _resolve_pdf_engine(self) -> PdfEngineResolution:
        engine = self._get_pdf_engine_config()
        pm_info = paper_muncher()
        if engine == "wkhtmltopdf":
            return PdfEngineResolution(engine, False, pm_info)
        if engine == "paper-muncher":
            if pm_info.state != "ok":
                raise UserError(
                    _(
                        "Paper-Muncher is not installed on this system. "
                        "Install it from "
                        "https://github.com/odoo/paper-muncher/releases "
                        "or set report.pdf_engine to 'auto' or 'wkhtmltopdf'."
                    )
                )
            return PdfEngineResolution(engine, True, pm_info)
        return PdfEngineResolution(engine, pm_info.state == "ok", pm_info)

    @api.model
    def _should_use_paper_muncher(self):
        return self._resolve_pdf_engine().use_paper_muncher

    @api.model
    def get_wkhtmltopdf_state(self):
        engine = self._get_pdf_engine_config()
        pm_info = paper_muncher()
        if engine == "wkhtmltopdf":
            return super().get_wkhtmltopdf_state()
        if pm_info.state == "ok":
            return "ok"
        if engine == "paper-muncher":
            return "install"
        return super().get_wkhtmltopdf_state()

    @api.model
    def _resolve_report_sudo(self, report_ref):
        if not report_ref:
            return None
        try:
            return self._get_report(report_ref)
        except ValueError:
            return None

    @api.model
    def _get_report_log_label(self, report_ref=False, report_sudo=None):
        if report_sudo:
            return report_sudo.report_name or report_sudo.display_name
        if not report_ref:
            return "unknown"
        try:
            report = self._get_report(report_ref)
            return report.report_name or report.display_name
        except ValueError:
            return str(report_ref)

    @api.model
    def _run_wkhtmltopdf(
        self,
        bodies,
        report_ref=False,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        resolution = self._resolve_pdf_engine()
        report_sudo = self._resolve_report_sudo(report_ref)
        report_label = self._get_report_log_label(report_ref, report_sudo=report_sudo)

        if resolution.use_paper_muncher:
            _logger.info(
                (
                    "PDF engine: Paper-Muncher "
                    "(report=%s, config=%s, binary=%s, version=%s)"
                ),
                report_label,
                resolution.engine,
                resolution.pm_info.bin,
                resolution.pm_info.version,
            )
            return self._run_paper_muncher(
                bodies,
                report_ref=report_ref,
                header=header,
                footer=footer,
                landscape=landscape,
                specific_paperformat_args=specific_paperformat_args,
                report_sudo=report_sudo,
                report_label=report_label,
                pm_info=resolution.pm_info,
            )
        if resolution.engine == "auto" and resolution.pm_info.state != "ok":
            _logger.info(
                (
                    "PDF engine: wkhtmltopdf "
                    "(report=%s, config=auto, Paper-Muncher not available)"
                ),
                report_label,
            )
        elif resolution.engine == "wkhtmltopdf":
            _logger.info(
                "PDF engine: wkhtmltopdf (report=%s, config=wkhtmltopdf)",
                report_label,
            )
        return super()._run_wkhtmltopdf(
            bodies,
            report_ref=report_ref,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )

    @api.model
    def _run_paper_muncher(
        self,
        bodies,
        report_ref=False,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        scale=72,
        report_sudo=None,
        report_label=None,
        pm_info=None,
    ):
        """Render a PDF from HTML content using Paper Muncher subprocess."""
        pm_info = pm_info or paper_muncher()
        report_label = report_label or self._get_report_log_label(
            report_ref, report_sudo=report_sudo
        )

        paperformat = (
            report_sudo.get_paperformat() if report_sudo else self.get_paperformat()
        )
        header = header or ""
        footer = footer or ""

        if not isinstance(bodies, list | tuple):
            bodies = list(bodies)

        documents = make_multi_docs_html(bodies, header, footer)

        names = [f"pipe:/paper-muncher/{i}.html" for i in range(len(documents))]
        extra_args = self._build_paper_muncher_extra_args(
            landscape=landscape,
            paperformat=paperformat,
            scale=scale,
            specific_paperformat_args=specific_paperformat_args,
        )

        os_env = os.environ.copy()
        os_env["NO_COLOR"] = "1"

        try:
            with ExitStack() as stack:
                wsgi_environ = {}
                if request and request.db:
                    temp_session = root.session_store.new()
                    temp_session.update(
                        {
                            **request.session,
                            "debug": "",
                            "_trace_disable": True,
                        }
                    )
                    if temp_session.uid:
                        temp_session.session_token = security.compute_session_token(
                            temp_session, self.env
                        )
                    root.session_store.save(temp_session)
                    stack.callback(root.session_store.delete, temp_session)
                    url = urlsplit(self._get_report_url())
                    wsgi_environ["HTTP_HOST"] = url.netloc
                    wsgi_environ["HTTP_COOKIE"] = (
                        f"session_id={temp_session.sid}; HttpOnly; "
                        f"domain={url.hostname}; path=/;"
                    )
                else:
                    wsgi_environ["HTTP_X_ODOO_DATABASE"] = self.env.cr.dbname

                with PaperMuncherServer(
                    args=[
                        pm_info.bin,
                        *names,
                        "-o",
                        "pipe:/paper-muncher/output.pdf",
                        *extra_args,
                    ],
                    os_env=os_env,
                    wsgi_environ=wsgi_environ,
                ) as server:
                    pdf = server.serve(documents)
                    _logger.info(
                        (
                            "PDF engine: Paper-Muncher completed "
                            "(report=%s, pages=%d, size=%d bytes)"
                        ),
                        report_label,
                        len(documents),
                        len(pdf),
                    )
                    return pdf
        except (subprocess.CalledProcessError, TimeoutError, RuntimeError) as exc:
            message = _("Paper-Muncher failed. Message: %s", str(exc)[-1000:])
            _logger.warning(message)
            raise UserError(message) from exc

    @api.model
    def _build_paper_muncher_extra_args(
        self,
        landscape=False,
        paperformat=None,
        scale=72,
        specific_paperformat_args=None,
    ):
        """Build paper-muncher CLI arguments (exposed for testing)."""
        if specific_paperformat_args:
            if not landscape and specific_paperformat_args.get("data-report-landscape"):
                landscape = specific_paperformat_args["data-report-landscape"]
            if specific_paperformat_args.get("data-report-dpi"):
                scale = int(specific_paperformat_args["data-report-dpi"])

        extra_args = [
            "--scale",
            f"{scale}dpi",
            "--margins",
            "none",
        ]
        if landscape:
            extra_args += ["--orientation", "landscape"]
        elif paperformat and paperformat.orientation:
            extra_args += ["--orientation", paperformat.orientation.lower()]
        if os.getenv("ODOO_PAPER_MUNCHER_FEATURE") == "1":
            extra_args += ["--feature", "*=on"]
        if paperformat and paperformat.format:
            if paperformat.format != "custom":
                extra_args += ["--paper", paperformat.format]
            elif paperformat.page_height and paperformat.page_width:
                extra_args += ["--width", f"{paperformat.page_width}mm"]
                extra_args += ["--height", f"{paperformat.page_height}mm"]
        if _paper_muncher_debug_enabled():
            extra_args += ["--debug", "http-client"]
        return extra_args
