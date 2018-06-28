# © 2014 David BEAL Akretion
# © 2016 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import re

from odoo import api, fields, models


class AbstractConfigSettings(models.AbstractModel):
    _name = 'abstract.config.settings'
    _description = 'Abstract configuration settings'
    # prefix field name to differentiate fields in company with those in config
    _prefix = 'setting_'
    # this is the class name to import in your module
    # (it should be ResCompany or res_company, depends of your code)
    _companyObject = None
    _setup_extra_done = False

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
        super(AbstractConfigSettings, self)._setup_base()
        if not cls._companyObject:
            return
        if cls._setup_extra_done:
            return
        for field_key in cls._companyObject.__dict__.keys():
            field = cls._companyObject.__dict__[field_key]
            if isinstance(field, fields.Field):
                # allows to exclude some field
                if self._filter_field(field_key):
                    # fields.agrs contains fields attributes
                    kwargs = field.args.copy()
                    kwargs['related'] = 'company_id.' + field_key
                    field_key = re.sub('^' + self._prefix, '', field_key)
                    self._add_field(field_key, field.new(**kwargs))
        cls._proper_fields = set(cls._fields)

        self._add_inherited_fields()
        cls.pool.model_cache[cls.__bases__] = cls
        cls._setup_extra_done = True
