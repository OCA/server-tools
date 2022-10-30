# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# Author Copyright (C) 2022 Appstogrow (Henrik Norlin) (henrik@appstogrow.co).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import models


class Base(models.AbstractModel):
    _inherit = "base"

    # This will make the parameters accessible from any Odoo model.
    def get_time_parameter(self, code, date_field_name=None, raise_if_not_found=True):
        if date_field_name and hasattr(self, date_field_name):
            date = getattr(self, date_field_name)
        else:
            date = None
        if type(date) is datetime.datetime:
            date = date.date()
        return self.env["base.time.parameter"]._get_value_from_model_code_date(
            self._name, code, date, raise_if_not_found=False
        )
