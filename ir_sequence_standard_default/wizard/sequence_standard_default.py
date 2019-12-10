# 2019  Vauxoo (<http://www.vauxoo.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from psycopg2.extensions import AsIs

from odoo import api, models

_logger = logging.getLogger(__name__)


class SequenceStandardDefault(models.TransientModel):

    _name = "sequence.standard.default"
    _description = "Wizard to set all sequences to Standard implementation"

    @api.model
    def change_all_sequences(self):
        sequences = self.env['ir.sequence'].sudo().with_context(
            active_test=False).search([('implementation', '=', 'no_gap')])
        _logger.info("Changing sequences to Standard: %s", sequences.ids)
        for item in sequences:
            seq_name = "ir_sequence_%03d" % (item.id)
            self._cr.execute("DROP SEQUENCE IF EXISTS %s", [AsIs(seq_name), ])
            if item.use_date_range:
                range_ids = {}
                for line in item.date_range_ids:
                    range_ids[line.id] = line.number_next_actual
                    seq_name = "ir_sequence_%03d_%03d" % (item.id, line.id)
                    self._cr.execute(
                        "DROP SEQUENCE IF EXISTS %s", [AsIs(seq_name), ])
                item.write({'implementation': 'standard'})
                for line in item.date_range_ids:
                    line.write({'number_next_actual': range_ids[line.id]})
                continue
            item.write({'implementation': 'standard'})

    @api.multi
    def execute(self):
        self.ensure_one()
        self.change_all_sequences()
        return self.env.ref('base.ir_sequence_form').read()[0]
