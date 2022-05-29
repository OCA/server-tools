# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# Author Copyright (C) 2022 appstogrow (Henrik Norlin) (henrik@appstogrow.co).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo import models

class Base(models.AbstractModel):
    _inherit = 'base'

    # This will make the parameters accessible from any Odoo model.
    def get_time_dependent_parameter(self, code, date=None):
        if not date:
            date = datetime.now().date

        return self.env["base.time_parameter"]._get_parameter_from_code(code, date)
