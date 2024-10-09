# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestTranslations(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestTranslations, cls).setUpClass()
        domain_fr = [("code", "=", "fr_FR")]
        cls.lang = cls.env["res.lang"].with_context(active_test=False).search(domain_fr)
        cls.lang.active = True
        cls.env["ir.translation"].load_module_terms(["base"], [cls.lang.code])

        def _irt(src, value, **params):
            model = cls.env["ir.translation"]
            if "context" in params:
                model = model.with_context(params.pop("context"))
            vals_base = {
                "type": "code",
                "name": "res.partner,signature",
                "module": "base_safe_translations_check",
                "lang": cls.lang.code,
                "state": "translated",
            }
            vals = {**vals_base, "src": src, "value": value, **params}
            return model.create(vals)

        cls._create_ir_translation = lambda self, *args, **kwargs: _irt(*args, **kwargs)
