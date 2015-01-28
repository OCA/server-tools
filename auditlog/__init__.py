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

from . import models


def pre_init_hook(cr):
    cr.execute("SELECT 1 FROM pg_class WHERE relname = 'audittrail_rule'")
    if cr.fetchall():
        migrate_from_audittrail(cr)


def migrate_from_audittrail(cr):
    cr.execute('ALTER TABLE audittrail_rule RENAME TO auditlog_rule')
    cr.execute('ALTER TABLE auditlog_rule RENAME COLUMN object_id TO model_id')
    cr.execute('ALTER TABLE audittrail_log RENAME TO auditlog_log')
    cr.execute('ALTER TABLE auditlog_log RENAME COLUMN object_id TO model_id')
    cr.execute('ALTER TABLE audittrail_log_line RENAME TO auditlog_log_line')
