# -*- coding: utf-8 -*-

# OpenERP, Open Source Management Solution
# This module copyright (C) 2013 Therp BV (<http://therp.nl>)
# Code snippets from openobject-server copyright (C) 2004-2013 OpenERP S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from openerp import _, api, exceptions, models, SUPERUSER_ID
from openerp.tools.safe_eval import safe_eval
from psycopg2 import OperationalError

_logger = logging.getLogger(__name__)


class Cron(models.Model):
    _name = _inherit = "ir.cron"

    @api.one
    def run_manually(self):
        """Run a job from the cron form view."""

        if self.env.uid != SUPERUSER_ID and (not self.active or
                                             not self.numbercall):
            raise exceptions.AccessError(
                _('Only the admin user is allowed to '
                  'execute inactive cron jobs manually'))

        try:
            # Try to grab an exclusive lock on the job row
            # until the end of the transaction
            self.env.cr.execute(
                """SELECT *
                   FROM ir_cron
                   WHERE id=%s
                   FOR UPDATE NOWAIT""",
                (self.id,),
                log_exceptions=False)

        except OperationalError as e:
            # User friendly error if the lock could not be claimed
            if getattr(e, "pgcode", None) == '55P03':
                raise exceptions.Warning(
                    _('Another process/thread is already busy '
                      'executing this job'))

            raise

        _logger.info('Job `%s` triggered from form', self.name)

        # Do not propagate active_test to the method to execute
        ctx = dict(self.env.context)
        ctx.pop('active_test', None)

        # Execute the cron job
        method = getattr(
            self.with_context(ctx).sudo(self.user_id).env[self.model],
            self.function)
        args = safe_eval('tuple(%s)' % (self.args or ''))
        return method(*args)

    @api.model
    def _current_uid(self):
        """This function returns the current UID, for testing purposes."""

        return self.env.uid
