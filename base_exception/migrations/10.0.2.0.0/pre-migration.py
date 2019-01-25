# -*- coding: utf-8 -*-
# © 2017 Akretion, Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    cr.execute("SELECT 1 FROM pg_class WHERE relname = 'sale_exception'")
    if openupgrade.table_exists('sale_exception'):
        openupgrade.rename_tables(cr, [('sale_exception', 'exception_rule')])

    except_model = env['ir.model'].search([('name', '=', 'sale.exception')])
    if len(except_model) == 1:
        openupgrade.rename_models(cr, [('sale.exception', 'exception.rule')])