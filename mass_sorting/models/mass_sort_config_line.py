# -*- coding: utf-8 -*-
##############################################################################
#
#    Mass Sorting Module for Odoo
#    Copyright (C) 2016-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

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
