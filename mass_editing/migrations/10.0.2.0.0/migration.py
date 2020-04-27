# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    if not version:
        return

    # Remove the obsolete constraint created by the existence of the
    # remove M2M field 'field_ids' between mass.object and ir.model.fields
    cr.execute(
        """
        DELETE FROM ir_model_relation
        WHERE name = 'mass_field_rel';
        """
    )

    migrated = False
    try:
        # Rename table for consistency reason
        cr.execute(
            """
            ALTER TABLE mass_object
            RENAME TO mass_editing;
        """
        )
    except Exception:
        # Table already migrated
        migrated = True

    if migrated:
        return

    # Create and Compute new required field
    cr.execute(
        """
        ALTER TABLE mass_editing
        ADD COLUMN action_name varchar;
    """
    )
    cr.execute(
        """
        UPDATE mass_editing
        SET action_name = name;
    """
    )
    cr.execute(
        """
        alter sequence mass_object_id_seq rename to mass_editing_id_seq;"""
    )

# Rename table for consistency reason
    cr.execute(
        """
        INSERT INTO mass_editing_line (mass_editing_id, field_id, widget_option)
            SELECT
                mass_id as mass_editing_id,
                field_id,
                CASE
                    WHEN ttype = 'many2one' THEN 'selection'
                    WHEN ttype = 'many2many' THEN 'many2many_tags'
                    WHEN (ttype = 'Binary'
                         AND (name LIKE '%image%' OR name LIKE '%logo%')) THEN 'image'
                    ELSE ''
                END as widget_option
            FROM mass_field_rel, ir_model_fields
            WHERE field_id = id;
    """
    )
