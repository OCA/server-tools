# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models

from ..tools import profiled


class EDIExchangeOutputTemplate(models.Model):
    _inherit = "edi.exchange.template.output"

    @profiled(sample_rate=1.0)
    def exchange_generate(self, exchange_record, **kw):
        """Generate output for given record using related QWeb template."""
        return super().exchange_generate(exchange_record, **kw)
