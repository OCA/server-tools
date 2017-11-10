# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


_field_renames = [
    ('mass.object', 'mass_object', 'ref_ir_act_window',
     'ref_ir_act_window_id'),
    ('mass.object', 'mass_object', 'ref_ir_value', 'ref_ir_value_id'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
