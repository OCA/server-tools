# -*- coding: utf-8 -*-
# Copyright 2017-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from psycopg2.extensions import AsIs

from odoo import _, api, fields, models


_logger = logging.getLogger(__name__)


SQL_SET_ACTIVE = \
    """UPDATE %(table)s
 SET active = true,
     active_change_datetime = %(change_datetime)s
 WHERE (active IS NULL OR NOT active)
   AND (%(date_start)s IS NULL OR %(date_start)s <= CURRENT_DATE)
   AND (%(date_end)s IS NULL OR %(date_end)s > CURRENT_DATE)"""

SQL_SET_INACTIVE = \
    """UPDATE %(table)s
 SET active = false,
     active_change_datetime = %(change_datetime)s
 WHERE (active IS NULL OR active)
   AND ((NOT %(date_start)s IS NULL AND %(date_start)s > CURRENT_DATE)
   OR (NOT %(date_end)s IS NULL AND %(date_end)s <= CURRENT_DATE))"""


class ActiveDate(models.AbstractModel):
    _name = 'active.date'
    _description = "Mixin for date dependend active"
    _field_date_start = "date_start"
    _field_date_end = "date_end"

    # We will not use _compute and a @depends method for active. Not
    # only because field might be changed by change of date, but also
    # because @depends method does not properly work for stored computed
    # fields.
    active = fields.Boolean(
        default=True,  # Only to provide initial value
        store=True,
        readonly=True,
        index=True,
        help="Active depends on start date, end date and current date")
    active_change_datetime = fields.Datetime(
        string='Timestamp active change',
        readonly=True,
        index=True,
        help="Technical field to select all records changed by the last"
             " run of active_refresh()")

    @api.multi
    def active_change_trigger(self):
        """Allows other models to react on change in active state.

        This method is meant to be overridden in other modules.
        """
        pass

    @api.multi
    def _compute_active(self):
        active_change_datetime = fields.Datetime.now()
        today = fields.Date.today()
        for this in self:
            save_active = this.active
            active = True
            start = this[self._field_date_start]
            end = this[self._field_date_end]
            if (start and start > today) or (end and end <= today):
                active = False
            if active != save_active:
                super(ActiveDate, this).write({
                    'active': active,
                    'active_change_datetime': active_change_datetime})
                this.active_change_trigger()

    @api.model
    def create(self, vals):
        new_rec = super(ActiveDate, self).create(vals)
        new_rec._compute_active()
        return new_rec

    @api.multi
    def write(self, vals):
        result = super(ActiveDate, self).write(vals)
        if self._field_date_start in vals or self._field_date_end in vals:
            self._compute_active()
        return result

    @api.model
    def active_refresh_post_process(self, active_change_datetime):
        """Postprocess records immediately after changing active field."""
        records = self.search([
            ('active_change_datetime', '=', active_change_datetime)])
        if records:
            records.active_change_trigger()

    @api.model
    def active_refresh(self):
        """Refresh the active field for all records where needed.

        For cases where there can be uncertainty wether the cron job has run,
        an on the fly recomputation is also possible.
        """
        def table_exists(cr, table):
            """ Check whether a certain table or view exists """
            cr.execute('SELECT 1 FROM pg_class WHERE relname = %s', (table,))
            return cr.fetchone()

        active_change_datetime = fields.Datetime.now()
        cr = self.env.cr
        if not table_exists(cr, self._table):
            _logger.debug(_("Table %s not in database."), self._table)
            return
        sql_parms = {
            'table': AsIs(self._table),
            'date_start': AsIs(self._field_date_start),
            'date_end': AsIs(self._field_date_end),
            'change_datetime': active_change_datetime}
        try:
            cr.execute(SQL_SET_ACTIVE, sql_parms)
        except Exception as e:
            _logger.error(_(
                "Exception when setting records to active for model %s:\n"
                "%s") % (self._name, e))
        try:
            cr.execute(SQL_SET_INACTIVE, sql_parms)
        except Exception as e:
            _logger.error(_(
                "Exception when setting records to inactive for model %s:\n"
                "%s") % (self._name, e))
        self.env.invalidate_all()  # Reset cache to force refresh from db
        self.active_refresh_post_process(active_change_datetime)

    @api.model
    def active_date_refresh_all_cron(self):
        """Compute active state.

        Although field active will be computed on create and each time
        start- or enddate changes, this is not enough, as the field is also
        dependent on the current date. Automatic recomputation is part of
        a cron job that should be run very close to but after midnight.
        """
        for model_name in self.env.registry.models:
            model = self.env[model_name]
            if hasattr(model, 'active_refresh'):
                _logger.info(_(
                    "Updating active field for model %s:") % model_name)
                model.active_refresh()
