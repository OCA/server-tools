# -*- coding: utf-8 -*-
# © 2017 Akretion, Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    if openupgrade.table_exists(cr, 'sale_exception'):
        openupgrade.rename_tables(cr, [('sale_exception', 'exception_rule')])
        openupgrade.rename_models(cr, [('sale.exception', 'exception.rule')])
