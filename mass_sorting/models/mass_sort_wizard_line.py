# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields
from openerp.osv.orm import TransientModel


class TransientModelLine(TransientModel):
    _name = 'mass.sort.wizard.line'

    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'wizard_id': fields.many2one(
            'mass.sort.wizard', string='Wizard'),
        'field_id': fields.many2one(
            'ir.model.fields', string='Field', required=True, domain="["
            "('model', '=', parent.one2many_model)]"),
        'desc': fields.boolean('Inverse Order'),
    }

    _defaults = {
        'sequence': 1,
    }
