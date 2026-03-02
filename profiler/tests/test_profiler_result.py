# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from unittest.mock import Mock, patch

from odoo.tests.common import TransactionCase


class TestProfilerResult(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.profiler_result_model = cls.env["profiler.result"]

    def _create_result(self, **vals):
        defaults = {
            "name": "test.function",
            "stats_text": "sample stats",
            "stats_binary": False,
        }
        defaults.update(vals)
        with self.env.norecompute():  # type: ignore[attr-defined]
            return self.profiler_result_model.create(defaults)

    def test_action_download_pstats_raises_without_binary(self):
        record = self._create_result(stats_binary=False)
        with self.assertRaises(ValueError):
            record.action_download_pstats()

    def test_action_download_callgrind_raises_without_data(self):
        record = self._create_result(stats_callgrind=False)
        with self.assertRaises(ValueError):
            record.action_download_callgrind()

    def test_action_download_urls(self):
        record = self._create_result(
            name="my.func",
            stats_binary=base64.b64encode(b"pstats").decode(),
            stats_callgrind=base64.b64encode(b"callgrind").decode(),
        )
        pstats_action = record.action_download_pstats()
        callgrind_action = record.action_download_callgrind()

        self.assertIn(
            f"/profiler.result/{record.id}/stats_binary/my.func.pstats",
            pstats_action["url"],
        )
        self.assertIn(
            f"/profiler.result/{record.id}/stats_callgrind/my.func.callgrind",
            callgrind_action["url"],
        )

    def test_generate_flamegraph_html_without_binary(self):
        record = self._create_result(stats_binary=False)
        html = record._generate_flamegraph_html()
        self.assertIn("No binary profiling data available", html)

    @patch("subprocess.run")
    def test_generate_flamegraph_flameprof_error_template(self, mock_run):
        mock_run.return_value = Mock(returncode=1, stderr="boom", stdout="")
        record = self._create_result(
            stats_binary=base64.b64encode(b"pstats").decode(),
        )

        html = record._generate_flamegraph_html()

        self.assertIn("Flamegraph Generation Failed", html)
        self.assertIn("boom", html)

    @patch("subprocess.run")
    def test_generate_flamegraph_flameprof_missing(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        record = self._create_result(
            stats_binary=base64.b64encode(b"pstats").decode(),
        )

        html = record._generate_flamegraph_html()

        self.assertIn("Flameprof Not Installed", html)

    @patch("subprocess.run")
    @patch("importlib.import_module")
    def test_generate_flamegraph_svg_fallback(self, mock_import_module, mock_run):
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="<svg><g/></svg>")
        mock_import_module.side_effect = ImportError()
        record = self._create_result(
            stats_binary=base64.b64encode(b"pstats").decode(),
        )

        html = record._generate_flamegraph_html()

        self.assertIn('<div class="flamegraph-wrapper">', html)
        self.assertIn("<svg><g/></svg>", html)

    @patch("subprocess.run")
    @patch("importlib.import_module")
    def test_generate_flamegraph_png_render(self, mock_import_module, mock_run):
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="<svg><g/></svg>")
        fake_cairosvg = Mock()
        fake_cairosvg.svg2png.return_value = b"png-bytes"
        mock_import_module.return_value = fake_cairosvg
        record = self._create_result(
            stats_binary=base64.b64encode(b"pstats").decode(),
        )

        html = record._generate_flamegraph_html()

        self.assertIn("data:image/png;base64,", html)
