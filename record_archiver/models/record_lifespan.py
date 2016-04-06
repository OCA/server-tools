# -*- coding: utf-8 -*-
# © 2015-2016 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import api, exceptions, fields, models
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class RecordLifespan(models.Model):
    """ Configure records lifespans per model

    After the lifespan is expired (compared to the `write_date` of the
    records), the records are deactivated.
    """
    _name = 'record.lifespan'
    _order = 'model'

    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        domain=[('has_an_active_field', '=', True)],
    )
    model = fields.Char(
        related='model_id.model',
        string='Model Name',
        store=True,
    )
    months = fields.Integer(
        required=True,
        help="Number of month after which the records will be set to inactive "
             "based on their write date"
    )

    _sql_constraints = [
        ('months_gt_0', 'check (months > 0)',
         "Months must be a value greater than 0"),
    ]

    @api.model
    def _scheduler_archive_records(self):
        lifespans = self.search([])
        _logger.info('Records archiver starts archiving records')
        for lifespan in lifespans:
            try:
                lifespan.archive_records()
            except exceptions.UserError as e:
                _logger.error("Archiver error:\n%s", e[1])
        _logger.info('Rusty Records now rest in peace')
        return True

    @api.multi
    def _archive_domain(self, expiration_date):
        """ Returns the domain used to find the records to archive.

        Can be inherited to change the archived records for a model.
        """
        model = self.env[self.model_id.model]
        domain = [('write_date', '<', expiration_date)]
        if 'state' in model._columns:
            domain += [('state', 'in', ('done', 'cancel'))]
        return domain

    @api.multi
    def _archive_lifespan_records(self):
        """ Archive the records for a lifespan, so for a model.

        Can be inherited to customize the archive strategy.
        The default strategy is to change the field ``active`` to False
        on the records having a ``write_date`` older than the lifespan.
        Only done and canceled records will be deactivated.

        """
        self.ensure_one()
        today = datetime.today()
        model_name = self.model_id.model
        model = self.env[model_name]
        if not isinstance(model, models.Model):
            raise exceptions.UserError(
                _('Model %s not found') % model_name)
        if 'active' not in model._columns:
            raise exceptions.UserError(
                _('Model %s has no active field') % model_name)

        delta = relativedelta(months=self.months)
        expiration_date = fields.Datetime.to_string(today - delta)

        domain = self._archive_domain(expiration_date)
        recs = model.search(domain)
        if not recs:
            return

        # use a SQL query to bypass tracking always messages on write for
        # object inheriting mail.thread
        query = ("UPDATE %s SET active = FALSE WHERE id in %%s"
                 ) % model._table
        self.env.cr.execute(query, (tuple(recs.ids),))
        recs.invalidate_cache()
        _logger.info(
            'Archived %s %s older than %s',
            len(recs.ids), model_name, expiration_date)

    @api.multi
    def archive_records(self):
        """ Call the archiver for several record lifespans """
        for lifespan in self:
            lifespan._archive_lifespan_records()
        return True
