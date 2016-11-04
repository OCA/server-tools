# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields
from openerp.osv.orm import Model


class MassSortConfigLine(Model):
    _name = 'mass.sort.config.line'
    _order = 'config_id, sequence, id'

    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'config_id': fields.many2one(
            'mass.sort.config', string='Wizard'),
        'field_id': fields.many2one(
            'ir.model.fields', string='Field', required=True, domain="["
            "('model', '=', parent.one2many_model)]"),
        'desc': fields.boolean('Inverse Order'),
    }

    _defaults = {
        'sequence': 1,
    }

    # Constraint Section
    def _check_field_id(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.field_id.model != line.config_id.one2many_model:
                return False
        return True

    _constraints = [
        (_check_field_id, "The selected criteria must belong to the parent"
            " model.", ['config_id', 'field_id']),
    ]
