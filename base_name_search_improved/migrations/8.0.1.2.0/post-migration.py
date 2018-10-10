# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV - http://therp.nl.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    cr.execute(
        'update ir_model set name_search_use_standard = true '
        'where name_search_use_standard is null'
    )
