# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from itertools import product

from .common import Common, PdfPipelineStopped


class TestBaseReportDeduplicateDocs(Common):
    """Checks the deduplication workflow"""

    def test_deduplicate_document_ids(self):
        """Duplicates are removed, order is kept, non-iterables are untouched"""
        self.report.deduplicate_docs = True
        self.assertEqual(
            self.report._deduplicate_document_ids(self.report, [3, 1, 3, 2, 1]),
            [3, 1, 2],
        )
        self.assertEqual(
            self.report._deduplicate_document_ids(self.report, (2, 2, 1)), [2, 1]
        )
        for res_ids in (None, [], 1):
            with self.subTest(res_ids=res_ids):
                self.assertEqual(
                    self.report._deduplicate_document_ids(self.report, res_ids), res_ids
                )

    def test_flag_disabled_keeps_duplicates(self):
        self.report.deduplicate_docs = False
        res_ids = [3, 1, 3, 2, 1]
        self.assertEqual(
            self.report._deduplicate_document_ids(self.report, res_ids), res_ids
        )

    def test_every_render_method_deduplicates(self):
        self.report.deduplicate_docs = True
        for name in self._get_render_method_names():
            with self.subTest(method=name):
                self._test_print_count(
                    method=name,
                    expected_subcontent_count=[
                        (self._doc_marker(1), 1),
                        (self._doc_marker(2), 1),
                    ],
                )

    def test_every_render_method_keeps_duplicates_when_disabled(self):
        self.report.deduplicate_docs = False
        for name in self._get_render_method_names():
            with self.subTest(method=name):
                self._test_print_count(
                    method=name,
                    expected_subcontent_count=[
                        (self._doc_marker(1), self.report_rec_ids.count(1)),
                        (self._doc_marker(2), self.report_rec_ids.count(2)),
                    ],
                )

    def test_report_deduplicate_content(self):
        """Ensures reports render as expected, according to the deduplication feature"""
        method_names = self._get_render_method_names()
        deduplicate_values = (False, True)
        for meth, dedup in product(method_names, deduplicate_values):
            with self.subTest(report_type=meth, deduplicate=dedup):
                self.report.deduplicate_docs = dedup
                rec_ids = [1, 1, 1, 2, 2, 2, 2]
                self._test_print_count(
                    method=meth,
                    rec_ids=rec_ids,
                    expected_subcontent_count=[
                        (self._doc_marker(1), 1 if dedup else rec_ids.count(1)),
                        (self._doc_marker(2), 1 if dedup else rec_ids.count(2)),
                    ],
                )

    def test_pdf_methods_deduplicate_without_wkhtmltopdf(self):
        """Checks the HTML bodies sent to wkhtmltopdf are deduplicated (or not)"""
        rec_ids = self.report_rec_ids
        for dedup, meth in product((True, False), self._get_render_pdf_method_names()):
            with self.subTest(deduplicate_docs=dedup, method=meth):
                self.report.deduplicate_docs = dedup
                with (
                    self._intercept_wkhtmltopdf() as bodies,
                    self.assertRaises(PdfPipelineStopped),
                ):
                    self._call_pdf_method(meth)
                count_1 = 1 if dedup else rec_ids.count(1)
                count_2 = 1 if dedup else rec_ids.count(2)
                # one HTML body per printed document
                self.assertEqual(len(bodies), count_1 + count_2)
                self._test_print_count_execute(
                    expected_subcontent_count=[
                        (self._doc_marker(1), count_1),
                        (self._doc_marker(2), count_2),
                    ],
                    content="".join(bodies),
                )
