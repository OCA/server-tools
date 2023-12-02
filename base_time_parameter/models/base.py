# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# Author Copyright (C) 2022 Appstogrow (Henrik Norlin) (henrik@appstogrow.co).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import models


class Base(models.AbstractModel):
    _inherit = "base"

    def get_time_parameter(self, code, date=None, raise_if_not_found=True, get="value"):
        if type(date) is str:
            # Get the date/datetime from a field on the record
            date = getattr(self, date)
        if type(date) is datetime.datetime:
            date = date.date()
        assert type(date) is datetime.date or date is None, "Wrong date"

        return self.env["base.time.parameter"]._get_from_model_code_date(
            self._name, code, date, raise_if_not_found=False, get=get
        )
