# -*- coding: utf-8 -*-
#
#    Author: Yannick Vaucher
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging

from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class RecordLifespan(orm.Model):
    """ Configure records lifespans per model

    After the lifespan is expired (compared to the `write_date` of the
    records), the records are deactivated.
    """
    _name = 'record.lifespan'

    _order = 'model'

    _columns = {
        'model_id': fields.many2one(
            'ir.model',
            string='Model',
            required=True,
            domain=[('has_an_active_field', '=', True)],
        ),
        'model': fields.related(
            'model_id', 'model',
            string='Model Name',
            type='char',
            readonly=True,
            store=True,
        ),
        'months': fields.integer(
            "Months",
            required=True,
            help="Number of month after which the records will be set to "
                 "inactive based on their write date"),
    }

    _sql_constraints = [
        ('months_gt_0', 'check (months > 0)',
         "Months must be a value greater than 0"),
    ]

    def _scheduler_archive_records(self, cr, uid, context=None):
        lifespan_ids = self.search(cr, uid, [], context=context)
        _logger.info('Records archiver starts archiving records')
        for lifespan_id in lifespan_ids:
            try:
                self.archive_records(cr, uid, [lifespan_id], context=context)
            except orm.except_orm as e:
                _logger.error("Archiver error:\n%s", e[1])
        _logger.info('Rusty Records now rest in peace')
        return True

    def _archive_domain(self, cr, uid, lifespan, expiration_date,
                        context=None):
        """ Returns the domain used to find the records to archive.

        Can be inherited to change the archived records for a model.
        """
        model = self.pool[lifespan.model]
        domain = [('write_date', '<', expiration_date),
                  ]
        if 'state' in model._columns:
            domain += [('state', 'in', ('done', 'cancel'))]
        return domain

    def _archive_lifespan_records(self, cr, uid, lifespan, context=None):
        """ Archive the records for a lifespan, so for a model.

        Can be inherited to customize the archive strategy.
        The default strategy is to change the field ``active`` to False
        on the records having a ``write_date`` older than the lifespan.
        Only done and canceled records will be deactivated.

        """
        today = datetime.today()
        model = self.pool.get(lifespan.model)
        if not model:
            raise orm.except_orm(
                _('Error'),
                _('Model %s not found') % lifespan.model)
        if 'active' not in model._columns:
            raise orm.except_orm(
                _('Error'),
                _('Model %s has no active field') % lifespan.model)

        delta = relativedelta(months=lifespan.months)
        expiration_date = (today - delta).strftime(DATE_FORMAT)

        domain = self._archive_domain(cr, uid, lifespan, expiration_date,
                                      context=context)
        rec_ids = model.search(cr, uid, domain, context=context)
        if not rec_ids:
            return

        # use a SQL query to bypass tracking always messages on write for
        # object inheriting mail.thread
        query = ("UPDATE %s SET active = FALSE WHERE id in %%s"
                 ) % model._table
        cr.execute(query, (tuple(rec_ids),))
        _logger.info(
            'Archived %s %s older than %s',
            len(rec_ids), lifespan.model, expiration_date)

    def archive_records(self, cr, uid, ids, context=None):
        """ Call the archiver for several record lifespans """
        for lifespan in self.browse(cr, uid, ids, context=context):
            self._archive_lifespan_records(cr, uid, lifespan, context=context)
        return True
