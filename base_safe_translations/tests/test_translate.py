# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .common import TestTranslations


class TestConstraints(TestTranslations):
    def test_nothing(self):
        # there is nothing, it should not cause any issue anyway
        self._create_ir_translation("Text.", "Texte.")

    def test_new_style_formatting(self):
        # modified internal formatting
        with self.assertRaises(ValidationError):
            self._create_ir_translation("Text {:0f}.", "Texte { :0f}.")
        # extraneous formatting argument
        with self.assertRaises(ValidationError):
            self._create_ir_translation("Text.", "Texte {:0f}.")
        # missing formatting argument
        with self.assertRaises(ValidationError):
            self._create_ir_translation("Text {}.", "Texte.")
        # inverted formatting arguments
        with self.assertRaises(ValidationError):
            self._create_ir_translation("Text {:0f} {}.", "Texte {} .{:0f}")

        # This works.
        self._create_ir_translation("Text {:2f} and {}.", "Texte {:2f} et {}.")

    def test_old_style_formatting(self):
        # modified internal formatting
        with self.assertRaises(ValidationError):
            self._create_ir_translation("Text %s.", "Texte %d.")
        # extraneous formatting argument
        with self.assertRaises(ValidationError):
            self._create_ir_translation("Text.", "Texte %s.")
        # missing formatting argument
        with self.assertRaises(ValidationError):
            self._create_ir_translation("Text %d.", "Texte.")
        # inverted formatting arguments
        with self.assertRaises(ValidationError):
            self._create_ir_translation("Text %s %d.", "Texte %d %s")

        # This works.
        self._create_ir_translation("Text %d and %s.", "Texte %d et %s.")

    def test_html_tags(self):
        # modified internal formatting
        with self.assertRaises(ValidationError):
            self._create_ir_translation("<i>Text</i>.", "<b>Texte<b>.")
        # extraneous formatting argument
        with self.assertRaises(ValidationError):
            self._create_ir_translation("Text.", "<i>Text</i>.")
        # missing formatting argument
        with self.assertRaises(ValidationError):
            self._create_ir_translation("<b>Text</b>.", "Texte.")
        # inverted formatting arguments
        with self.assertRaises(ValidationError):
            self._create_ir_translation("<b><i>Text</i></b>.", "<i><b>Text</b></i>")

        # This works.
        self._create_ir_translation("<i><b>Text</b></i>", "<i><b>Texte</b></i>")
