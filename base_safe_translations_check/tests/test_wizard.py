# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tools import mute_logger

from .common import TestTranslationsWizard


class TestTranslationsWizardFlow(TestTranslationsWizard):
    @mute_logger("odoo.addons.queue_job.models.base")
    def test_faulty_translation(self):
        lang = self.env.ref("base.lang_fr")
        vals = {"module": "base_safe_translations_check", "lang_id": lang.id}
        wizard = self.env["ir.translation.safe.wizard"].create(vals)

        with self.assertRaises(ValidationError):
            wizard.with_context(test_queue_job_no_delay=True)._execute()

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_all_right(self):
        module = "module"
        module_name = "base_safe_translations"
        domain = [("value", "not in", [False, ""]), (module, "=", module_name)]
        translations_nmbr = self.env["ir.translation"].search_count(domain)
        wizard = self.env["ir.translation.safe.wizard"].create({module: module_name})

        res = wizard.with_context(test_queue_job_no_delay=True)._execute()

        self.assertEqual(len(res), translations_nmbr)
