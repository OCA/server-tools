# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_safe_translations.tests.common import TestTranslations


class TestTranslationsWizard(TestTranslations):
    @classmethod
    def setUpClass(cls):
        super(TestTranslationsWizard, cls).setUpClass()
        cls.translated_term = cls._create_ir_translation(
            False, "Oh {}", "Ho {}", module="base_safe_translations_check"
        )
        # we force a wrong translation in database
        query = 'UPDATE ir_translation SET "value"=%s WHERE id = %s'
        params = ("Ho non", cls.translated_term.id)
        cls.env.cr.execute(query, params)
