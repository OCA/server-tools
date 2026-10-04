# Copyright 2026 CORSA.pro (https://www.corsa.pro)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import importlib.util
import pathlib
import re

from odoo.tests import TransactionCase, tagged
from odoo.tools.misc import file_open, file_path

EDITOR_CSS = "base_fontawesome/static/src/css/fontawesome_editor.css"
COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")


def rule(css, name):
    """(names, declarations) of the rule holding ``.fa-<name>::before``."""
    for selectors, body in RULE.findall(COMMENT.sub("", css)):
        names = [part.strip()[4:-8] for part in selectors.split(",")]
        if name in names:
            return names, " ".join(body.split())
    return [], ""


@tagged("post_install", "-at_install")
class TestEditorCss(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with file_open(EDITOR_CSS) as css_file:
            cls.css = css_file.read()

    def test_loaded_in_the_backend(self):
        paths = [
            asset[0]
            for asset in self.env["ir.asset"]._get_asset_paths("web.assets_backend", {})
        ]
        self.assertIn(f"/{EDITOR_CSS}", paths)

    def test_aliases_share_a_rule_shortest_name_first(self):
        names, declarations = rule(self.css, "magnifying-glass")
        # The editor shows the first name: Odoo's own, here.
        self.assertEqual(names[0], "search")
        self.assertEqual(declarations, 'content: "\\f002";')

    def test_v4_names_keep_their_v4_icon(self):
        # Font Awesome 6 redefines "repeat"; "fa fa-repeat" still draws the
        # v4 icon through v4-shims.css.
        self.assertIn('content: "\\f01e";', rule(self.css, "repeat")[1])
        self.assertIn('content: "\\f000";', rule(self.css, "glass")[1])

    def test_styles_are_kept_apart(self):
        # Same glyph, regular style: its own rule and weight.
        heart_o = rule(self.css, "heart-o")
        self.assertNotIn("heart", heart_o[0])
        self.assertIn("font-weight: 400;", heart_o[1])
        # Brand icons draw with the brands font, with "fa fa-name" too.
        self.assertIn(
            'font-family: "Font Awesome 6 Brands";', rule(self.css, "x-twitter")[1]
        )
        self.assertNotIn("font-family", rule(self.css, "car")[1])

    def test_up_to_date_with_the_bundled_font_awesome(self):
        script = pathlib.Path(file_path("base_fontawesome/scripts/build_editor_css.py"))
        spec = importlib.util.spec_from_file_location("build_editor_css", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        (lib,) = sorted((script.parent.parent / "static/lib").glob("fontawesome-*"))
        content, _names, _glyphs = module.build(lib)
        self.assertEqual(content, self.css, "Run scripts/build_editor_css.py")
