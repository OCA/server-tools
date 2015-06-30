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

from openerp.osv import orm, fields, osv
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
        'model': fields.char(
            "Model",
            required=True),
        'months': fields.integer(
            "Months",
            required=True,
            help="Number of month after which the records will be set to "
                 "inactive based on their write date"),
        'company_id': fields.many2one(
            'res.company',
            string="Company",
            ondelete="cascade",
            required=True),
    }

    _sql_constraints = [
        ('model_uniq', 'unique(model, company_id)',
         "A model can only have 1 lifespan per company"),
        ('months_gt_0', 'check (months > 0)',
         "Months must be a value greater than 0"),
    ]

    def _scheduler_record_archiver(self, cr, uid, context=None):
        lifespan_ids = self.search(cr, uid, [], context=context)
        _logger.info('Records archiver starts archiving records')
        for lifespan_id in lifespan_ids:
            try:
                self.archive_records(cr, uid, [lifespan_id], context=context)
            except osv.except_osv as e:
                _logger.error("Archiver error:\n%s", e[1])
        _logger.info('Rusty Records now rest in peace')
        return True

    def archive_records(self, cr, uid, ids, context=None):
        """ Search and deactivate old records for each configured lifespan

        Only done and cancelled records will be deactivated.
        """
        lifespans = self.browse(cr, uid, ids, context=context)
        today = datetime.today()
        for lifespan in lifespans:

            model = self.pool[lifespan.model]
            if not model:
                raise osv.except_osv(
                    _('Error'),
                    _('Model %s not found') % lifespan.model)
            if 'active' not in model._columns.keys():
                raise osv.except_osv(
                    _('Error'),
                    _('Model %s has no active field') % lifespan.model)
            delta = relativedelta(months=lifespan.months)
            expiration_date = (today - delta).strftime(DATE_FORMAT)
            domain = [('write_date', '<', expiration_date),
                      ('company_id', '=', lifespan.company_id.id)]
            if 'state' in model._columns.keys():
                domain += [('state', 'in', ('done', 'cancel'))]
            rec_ids = model.search(cr, uid, domain, context=context)

            if not rec_ids:
                continue
            # use a SQL query to bypass tracking always messages on write for
            # object inheriting mail.thread
            query = ("UPDATE %s SET active = FALSE WHERE id in %%s"
                     ) % model._table
            cr.execute(query, (tuple(rec_ids),))
            _logger.info(
                'Archived %s %s older than %s',
                len(rec_ids), lifespan.model, expiration_date)
