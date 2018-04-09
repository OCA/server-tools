# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from odoo.addons.base_binary_validation.fields import BinaryValidated


class TestModelMixin(object):

    @classmethod
    def _test_setup(cls, env):
        cls._build_model(env.registry, env.cr)
        env.registry.setup_models(env.cr)
        env.registry.init_models(
            env.cr, [cls._name],
            dict(env.context, update_custom_fields=True)
        )

    @classmethod
    def _test_teardown(cls, env):
        if not getattr(cls, '_teardown_no_delete', False):
            del env.registry.models[cls._name]
        env.registry.setup_models(env.cr)


class FakeModel(models.Model, TestModelMixin):
    _name = 'binary.fake.model'

    name = fields.Char()
    pdf_file = BinaryValidated(
        string='Terms and Conditions',
        attachment=True,
        allowed_mimetypes=('application/pdf', 'application/octet-stream', ),
    )
    text_file = BinaryValidated(
        string='Terms and Conditions',
        attachment=True,
        allowed_mimetypes=('text/plain', ),
    )
