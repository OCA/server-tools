# -*- coding: utf-8 -*-
# © 2015 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import models


def pre_init_hook(cr):
    cr.execute("SELECT 1 FROM pg_class WHERE relname = 'audittrail_rule'")
    if cr.fetchall():
        migrate_from_audittrail(cr)


def migrate_from_audittrail(cr):
    cr.execute('ALTER TABLE audittrail_rule RENAME TO auditlog_rule')
    cr.execute('ALTER TABLE audittrail_rule_id_seq '
               'RENAME TO auditlog_rule_id_seq')
    cr.execute('ALTER TABLE auditlog_rule RENAME COLUMN object_id TO model_id')
    cr.execute('ALTER TABLE audittrail_log RENAME TO auditlog_log')
    cr.execute('ALTER TABLE audittrail_log_id_seq '
               'RENAME TO auditlog_log_id_seq')
    cr.execute('ALTER TABLE auditlog_log RENAME COLUMN object_id TO model_id')
    cr.execute('ALTER TABLE audittrail_log_line RENAME TO auditlog_log_line')
    cr.execute('ALTER TABLE audittrail_log_line_id_seq '
               'RENAME TO auditlog_log_line_id_seq')
    cr.execute("UPDATE ir_model_data SET model='auditlog.rule' "
               "WHERE model='audittrail.rule'")
