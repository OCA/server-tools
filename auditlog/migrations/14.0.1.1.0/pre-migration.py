# © 2018 Pieter Paulussen <pieter_paulussen@me.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging


def migrate(cr, version):
    if not version:
        return
    logger = logging.getLogger(__name__)
    logger.info(
        "Creating columns: auditlog_log (model_name, model_model) "
        "and auditlog_log_line (field_name, field_description)."
    )
    cr.execute(
        """
    ALTER TABLE auditlog_log
    ADD COLUMN IF NOT EXISTS model_name VARCHAR,
    ADD COLUMN IF NOT EXISTS model_model VARCHAR;
    ALTER TABLE auditlog_log_line
    ADD COLUMN IF NOT EXISTS field_name VARCHAR,
    ADD COLUMN IF NOT EXISTS field_description VARCHAR;
    ALTER TABLE auditlog_rule
    ADD COLUMN IF NOT EXISTS model_name VARCHAR,
    ADD COLUMN IF NOT EXISTS model_model VARCHAR;
    """
    )
    logger.info(
        "Creating indexes on auditlog_log column 'model_id' and "
        "auditlog_log_line column 'field_id'."
    )
    cr.execute(
        """
        CREATE INDEX IF NOT EXISTS
        auditlog_log_model_id_index ON auditlog_log (model_id);
        CREATE INDEX IF NOT EXISTS
        auditlog_log_line_field_id_index ON auditlog_log_line (field_id);
    """
    )
    logger.info(
        "Preemptive fill auditlog_log columns: 'model_name' and " "'model_model'."
    )
    cr.execute(
        """
    UPDATE auditlog_log al
    SET model_name = im.name, model_model = im.model
    FROM ir_model im
    WHERE im.id = al.model_id AND model_name IS NULL
    """
    )
    logger.info(
        "Preemtive fill of auditlog_log_line columns: 'field_name' and"
        " 'field_description'."
    )
    cr.execute(
        """
    UPDATE auditlog_log_line al
    SET field_name = imf.name, field_description = imf.field_description
    FROM ir_model_fields imf
    WHERE imf.id = al.field_id AND field_name IS NULL
    """
    )
    logger.info(
        "Preemptive fill auditlog_rule columns: 'model_name' and " "'model_model'."
    )
    cr.execute(
        """
    UPDATE auditlog_rule al
    SET model_name = im.name, model_model = im.model
    FROM ir_model im
    WHERE im.id = al.model_id AND model_name IS NULL
    """
    )
    logger.info("Successfully updated auditlog tables")
