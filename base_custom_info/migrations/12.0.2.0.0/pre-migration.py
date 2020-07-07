# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if not openupgrade.column_exists(
        cr,
        'custom_info_property',
        'widget'
    ):
        openupgrade.add_fields(
            env,
            [('widget', 'custom.info.property', 'custom_info_property', 'char',
              False, 'base_custom_info')]
        )
        transform_values = [
            ('str', 'char'),
            ('int', 'integer'),
            ('bool', 'boolean'),
            ('float', 'float'),
            ('id', 'many2one')
        ]
        for field_type, widget in transform_values:
            cr.execute(
                "UPDATE custom_info_property SET widget = %s WHERE "
                "field_type = %s",
                (widget, field_type)
            )
