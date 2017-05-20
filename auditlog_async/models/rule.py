# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ABF OSIELL (<http://osiell.com>).
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

from openerp import models

from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession


@job
def delay_create_logs(
        session, uid, res_model, res_ids, method,
        old_values, new_values, additional_log_values):
    rule_model = session.env['auditlog.rule']
    rule_model.with_context(auditlog_delay_log_creation=True).create_logs(
        uid, res_model, res_ids, method,
        old_values, new_values, additional_log_values)


class Rule(models.Model):
    _inherit = 'auditlog.rule'

    def create_logs(self, uid, res_model, res_ids, method,
                    old_values=None, new_values=None,
                    additional_log_values=None):
        if self.env.context.get('auditlog_delay_log_creation'):
            super(Rule, self).create_logs(
                uid, res_model, res_ids, method,
                old_values, new_values, additional_log_values)
        else:
            session = ConnectorSession(
                self.env.cr, self.env.uid, self.env.context)
            delay_create_logs.delay(
                session, uid, res_model, res_ids, method,
                old_values, new_values, additional_log_values)
