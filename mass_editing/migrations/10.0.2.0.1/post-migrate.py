# -*- coding: utf-8 -*-
# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    if not version:
        return
    # Move field_ids to mass_editing_line
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

    cr.execute(
        """
        DELETE FROM ir_model_relation
        WHERE name = 'mass_field_rel';
        """
    )
