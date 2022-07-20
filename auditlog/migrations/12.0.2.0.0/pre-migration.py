# Copyright 2022 Hunki Enterprises BV (<https://hunki-enterprises.com>)


def migrate(cr, version=None):
    """ delete all logs of fields called 'password' as we ignore them from now on """
    cr.execute(
        "delete from auditlog_log_line al using ir_model_fields imf "
        "where al.field_id=imf.id and imf.name='password'"
    )
