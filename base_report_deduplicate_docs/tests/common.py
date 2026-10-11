# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from contextlib import contextmanager
from textwrap import dedent
from unittest.mock import patch

from odoo import models
from odoo.tests.common import TransactionCase, tagged


class PdfPipelineStopped(Exception):
    """Raised by the fake ``_run_wkhtmltopdf()`` to stop the pipeline there"""


@tagged("post_install", "-at_install")
class Common(TransactionCase):
    # ---------------------------------------------------------------------------------
    # Setup
    # ---------------------------------------------------------------------------------

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.report = cls._setup_report()
        cls.template = cls._setup_template()
        cls.report_rec_ids = cls._setup_report_rec_ids()
        cls.report_data = cls._setup_report_data()

    @classmethod
    def _setup_report(cls):
        return cls.env["ir.actions.report"].create(
            [
                {
                    "name": "Test Report",
                    "model": "res.partner",
                    "report_name": "test_report.test_report",
                    "paperformat_id": cls.env.ref("base.paperformat_euro").id,
                }
            ]
        )

    @classmethod
    def _setup_template(cls):
        return cls.env["ir.ui.view"].create(
            [
                {
                    "type": "qweb",
                    "name": "test_report_partner",
                    "key": "test_report.test_report",
                    "arch": dedent(
                        """
<t t-call="web.html_container">
    <t t-foreach="docs" t-as="o">
        <div class="article"
             t-att-data-oe-model="o._name"
             t-att-data-oe-id="o.id"
             t-att-data-oe-lang="o.env.context.get('lang')">
            <span class="test-doc-id"><t t-out="o.id"/></span>
        </div>
    </t>
</t>
                        """
                    ).strip(),
                }
            ]
        )

    @classmethod
    def _setup_report_rec_ids(cls):
        return [1, 1, 1, 2, 2, 2, 2]

    @classmethod
    def _setup_report_data(cls):
        return {}

    # ---------------------------------------------------------------------------------
    # Test tools
    # ---------------------------------------------------------------------------------

    def _test_print_count(
        self,
        /,
        expected_subcontent_count: list[tuple[str, int]],
        report: models.Model | str | int | None = None,
        rec_ids: list[int] | None = None,
        data: dict | None = None,
        method: str | None = None,
        **kwargs,  # Unused for now, improves heritability
    ):
        """Tests reports are generated w/ correct count of items

        Runs ``report._render*()`` and checks how many times each sub-content appears
        in the rendered report content.

        :param expected_subcontent_count: an iterable of couples (str, int), where the
            first element of the couple is the subcontent that needs to be found
            inside the report content, and the second element is how many times we
            expect to find it
        :param report: an ``ir.actions.report`` record, a ``str`` or an ``int`` to
            pass to ``ir.actions.report._get_report()``; if not provided, defaults to
            ``self.report``
        :param rec_ids: a list of record IDs to pass to ``report._render()``; if not
            provided, defaults to ``self.report_rec_ids``
        :param data: a dict of info to pass to ``report._render()``; if not provided,
            defaults to ``self.report_data``
        """
        execute_kwargs = self._test_print_count_setup(
            expected_subcontent_count=expected_subcontent_count,
            report=report,
            rec_ids=rec_ids,
            data=data,
            method=method,
            **kwargs,
        )
        self._test_print_count_execute(**execute_kwargs)

    def _test_print_count_setup(
        self,
        /,
        expected_subcontent_count: list[tuple[str, int]],
        report: models.Model | str | int | None = None,
        rec_ids: list[int] | None = None,
        data: dict | None = None,
        method: str | None = None,
        **kwargs,  # Unused for now, improves heritability
    ):
        """Sets up the test parameters for ``_test_print_count_execute()``"""
        if report:
            report = self.env["ir.actions.report"]._get_report(report)
        else:
            report = self.report
        rec_ids = rec_ids or self.report_rec_ids
        data = dict(data or self.report_data)
        method = method or "_render"
        # Rendering methods don't share parameter names (``res_ids`` vs ``docids``),
        # so arguments are passed positionally
        content = getattr(report, method)(report, rec_ids, data)[0].decode("utf-8")
        setup_kwargs = {
            "expected_subcontent_count": expected_subcontent_count,
            "content": content,
            "report": report,
            "rec_ids": rec_ids,
            "data": data,
            "method": method,
        }
        return setup_kwargs | kwargs

    def _test_print_count_execute(
        self,
        /,
        expected_subcontent_count: list[tuple[str, int]],
        content: str,
        report: models.Model | str | int | None = None,
        rec_ids: list[int] | None = None,
        data: dict | None = None,
        method: str | None = None,
        **kwargs,  # Unused for now, improves heritability
    ):
        """Tests reports are generated w/ correct count of items

        Runs ``report._render*()`` and checks how many times each sub-content appears
        in the rendered report content.

        :param expected_subcontent_count: an iterable of couples (str, int), where the
            first element of the couple is the subcontent that needs to be found
            inside the report content, and the second element is how many times we
            expect to find it
        :param report: an ``ir.actions.report`` record, a ``str`` or an ``int`` to
            pass to ``ir.actions.report._get_report()``; if not provided, defaults to
            ``self.report``
        :param rec_ids: a list of record IDs to pass to ``report._render()``; if not
            provided, defaults to ``self.report_rec_ids``
        :param data: a dict of info to pass to ``report._render()``; if not provided,
            defaults to ``self.report_data``
        """
        for expected_subcontent, expected_count in expected_subcontent_count:
            self.assertEqual(content.count(expected_subcontent), expected_count)

    # ---------------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------------

    @staticmethod
    def _get_render_method_names() -> tuple[str, ...]:
        """Methods returning ``(content, type)``, testable by ``_test_print_count()``"""
        return "_render", "_render_qweb_html", "_render_qweb_pdf", "_render_qweb_text"

    @staticmethod
    def _get_render_pdf_method_names() -> tuple[str, ...]:
        """Methods involving ``wkhtmltopdf`` testable by ``_test_print_count()``"""
        return (
            "_pre_render_qweb_pdf",
            "_render_qweb_pdf",
            "_render_qweb_pdf_prepare_streams",
        )

    @staticmethod
    def _doc_marker(doc_id: int) -> str:
        """The HTML snippet the test template renders for a document"""
        return f'<span class="test-doc-id">{doc_id}</span>'

    @contextmanager
    def _intercept_wkhtmltopdf(self):
        """Stops PDF rendering right before wkhtmltopdf would be called

        Replaces ``get_wkhtmltopdf_state()`` (so a missing binary doesn't matter)
        and ``_run_wkhtmltopdf()`` (which records the HTML bodies it receives), and
        raises ``PdfPipelineStopped``. Yields the list of recorded bodies.
        """
        bodies_seen = []

        def fake_get_state(model):
            return "ok"

        def fake_run(model, bodies, *args, **kwargs):
            bodies_seen.extend(str(body) for body in bodies)
            raise PdfPipelineStopped()

        cls = type(self.env["ir.actions.report"])
        with (
            patch.object(cls, "get_wkhtmltopdf_state", fake_get_state),
            patch.object(cls, "_run_wkhtmltopdf", fake_run),
        ):
            yield bodies_seen

    def _call_pdf_method(self, method: str):
        """Calls a PDF rendering method, bypassing the test-mode fallback to HTML"""
        # ``force_report_rendering`` disables the fallback to ``_render_qweb_html()``
        # that Odoo does by default when running tests
        model = self.env["ir.actions.report"].with_context(force_report_rendering=True)
        rec_ids = list(self.report_rec_ids)
        data = dict(self.report_data)
        if method == "_render_qweb_pdf_prepare_streams":
            # this method takes ``data`` before ``res_ids``
            return getattr(model, method)(self.report, data, rec_ids)
        return getattr(model, method)(self.report, rec_ids, data)
