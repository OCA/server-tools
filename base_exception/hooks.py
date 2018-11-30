# -*- coding: utf-8 -*-
# Copyright 2017 Akretion, Mourad EL HADJ MIMOUNE
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def pre_init_hook(cr):
    """If coming from v9 where only `sale_exception` is installed, when
    auto-installing this one by dependencies, we should take care of
    renaming previous table before the new model is loaded.
    """
    cr.execute("SELECT 1 FROM pg_class WHERE relname = 'sale_exception'")
    if not cr.fetchone():
        return  # fresh install, so exiting
    from openupgradelib import openupgrade
    openupgrade.rename_tables(cr, [('sale_exception', 'exception_rule')])
    openupgrade.rename_models(cr, [('sale.exception', 'exception.rule')])
