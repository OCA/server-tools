# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.http import request
from openerp.addons.web.controllers.main import Export
from ..models.restrict_field_access_mixin import RestrictFieldAccessMixin


class RestrictedExport(Export):
    """Don't (even offer to) export inaccessible fields"""
    def fields_get(self, model):
        fields = super(RestrictedExport, self).fields_get(model)
        model = request.env[model]
        if isinstance(model, RestrictFieldAccessMixin):
            sanitised_fields = {
                k: fields[k] for k in fields
                if model._restrict_field_access_is_field_accessible(k)
            }
            return sanitised_fields
        else:
            return fields
