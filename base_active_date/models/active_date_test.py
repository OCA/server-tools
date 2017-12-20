# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models, _


_logger = logging.getLogger(__name__)


class ActiveDateTest(models.Model):
    _name = 'active.date.test'
    _inherit = ['active.date']
    _description = "Just for testing active.date"
    _field_date_start = 'date_begin'
    _field_date_end = 'date_stop'

    code = fields.Char()
    name = fields.Char()
    date_begin = fields.Date()
    date_stop = fields.Date()

    @api.multi
    def active_change_trigger(self):
        """Log how many records of table changed."""
        super(ActiveDateTest, self).active_change_trigger()
        _logger.info(_(
            "active_change_trigger called on %s for %d records"),
            self._table, len(self))
