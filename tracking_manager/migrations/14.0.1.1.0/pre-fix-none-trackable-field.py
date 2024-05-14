#!/usr/bin/python3
# pylint: disable=print-used


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_model_fields
        SET custom_tracking=False
        WHERE trackable=False
        """
    )
