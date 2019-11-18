# © 2014 David BEAL Akretion
# © 2016 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import re

from odoo import api, fields, models
from inspect import getmembers


class AbstractConfigSettings(models.AbstractModel):
    _name = 'abstract.config.settings'
    _description = 'Abstract configuration settings'
    # prefix field name to differentiate fields in company with those in config
    _prefix = 'setting_'

    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=lambda self: self.env.user.company_id
    )

    def _filter_field(self, field_key):
        """Inherit in your module to define for which company field
        you don't want have a matching related field"""
        return True

    @api.model
    def _setup_base(self):
        cls = type(self)
        super()._setup_base()

        comp_fields = filter(
            lambda f: (f[0].startswith(self._prefix) and
                       self._filter_field(f[0])),
            getmembers(type(self.env['res.company']),
                       fields.Field.__instancecheck__)
        )

        for field_key, field in comp_fields:
            kwargs = field.args.copy()
            kwargs['related'] = 'company_id.' + field_key
            kwargs['readonly'] = False
            field_key = re.sub('^' + self._prefix, '', field_key)
            self._add_field(field_key, field.new(**kwargs))
        cls._proper_fields = set(cls._fields)

        self._add_inherited_fields()
        cls.pool.model_cache[cls.__bases__] = cls
