# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

class Base(models.AbstractModel):
    _inherit = 'base'

    # This will make the parameters accessible from any Odoo model.
    def get_time_dependent_parameter(self, code):
        return self.env["base.time.dependent.parameter"]._get_parameter_from_code(code, self.dict.date_to)
