# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>)
#    Code snippets from openobject-server copyright (C) 2004-2013 OpenERP S.A.
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
##############################################################################

import psycopg2
import logging
from openerp.osv import orm
from openerp.tools import SUPERUSER_ID
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval


class irCron(orm.Model):
    _inherit = 'ir.cron'

    def run_manually(self, cr, uid, ids, context=None):
        """
        Run a job from the cron form view.

        Cut and paste of code snippets from addons/base/ir/ir_cron.py
        """
        logger = logging.getLogger('cron_run_manually')
        cr.execute(
            """
            SELECT * from ir_cron
            WHERE id in %s
            """, (tuple(ids),))
        jobs = cr.dictfetchall()

        for job in jobs:
            if uid != SUPERUSER_ID and (
                    not job['active'] or not job['numbercall']):
                raise orm.except_orm(
                    _('Error'),
                    _('Only the admin user is allowed to '
                      'execute inactive cron jobs manually'))

            try:
                # Try to grab an exclusive lock on the job row
                # until the end of the transaction
                cr.execute(
                    """SELECT *
                       FROM ir_cron
                       WHERE id=%s
                       FOR UPDATE NOWAIT""",
                    (job['id'],), log_exceptions=False)

                # Got the lock on the job row, run its code
                logger.debug('Job `%s` triggered from form', job['name'])
                model = self.pool.get(job['model'])
                method = getattr(model, job['function'])
                args = safe_eval('tuple(%s)' % (job['args'] or ''))
                method(cr, job['user_id'], *args)

            except psycopg2.OperationalError as e:
                # User friendly error if the lock could not be claimed
                if e.pgcode == '55P03':
                    raise orm.except_orm(
                        _('Error'),
                        _('Another process/thread is already busy '
                          'executing this job'))
                raise

        return True
