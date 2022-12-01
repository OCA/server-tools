# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

field_spec = [
    (
        "name",
        "auditlog.log.line",
        "auditlog_log_line",
        "char",
        False,
        "auditlog",
    ),
    (
        "model_id",
        "auditlog.log.line",
        "auditlog_log_line",
        "many2one",
        False,
        "auditlog",
    ),
    (
        "model_name",
        "auditlog.log.line",
        "auditlog_log_line",
        "char",
        False,
        "auditlog",
    ),
    (
        "model_model",
        "auditlog.log.line",
        "auditlog_log_line",
        "char",
        False,
        "auditlog",
    ),
    (
        "res_id",
        "auditlog.log.line",
        "auditlog_log_line",
        "integer",
        False,
        "auditlog",
    ),
    (
        "user_id",
        "auditlog.log.line",
        "auditlog_log_line",
        "many2one",
        False,
        "auditlog",
    ),
    (
        "method",
        "auditlog.log.line",
        "auditlog_log_line",
        "char",
        False,
        "auditlog",
    ),
    (
        "http_session_id",
        "auditlog.log.line",
        "auditlog_log_line",
        "many2one",
        False,
        "auditlog",
    ),
    (
        "http_request_id",
        "auditlog.log.line",
        "auditlog_log_line",
        "many2one",
        False,
        "auditlog",
    ),
    (
        "log_type",
        "auditlog.log.line",
        "auditlog_log_line",
        "selection",
        False,
        "auditlog",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, field_spec)
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE auditlog_log_line aull
        SET name = al.name,
            model_id = al.model_id,
            model_name = al.model_name,
            model_model = al.model_model,
            res_id = al.res_id,
            user_id = al.user_id,
            method = al.method,
            http_session_id = al.http_session_id,
            http_request_id = al.http_request_id,
            log_type = al.log_type
        FROM auditlog_log al
        WHERE aull.log_id = al.id
        """,
    )
