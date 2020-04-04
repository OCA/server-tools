# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init_hook(cr, pool):
    """ Post installation hooks """
    add_default_val(cr)


def add_default_val(cr):
    # Set database default of the field to True,
    # setting the Odoo default is not enough unfortunately
    # https://github.com/OCA/OCB/blob/8.0/openerp/models.py#L377
    cr.execute('''
        ALTER TABLE ir_model
        ALTER COLUMN name_search_use_standard
        SET DEFAULT True
    ''')
