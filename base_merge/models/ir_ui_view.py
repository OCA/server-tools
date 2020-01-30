# -*- coding: utf-8 -*-
# © 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class View(models.Model):
    
    _inherit = 'ir.ui.view'
    
    def postprocess(
        self,
        model, 
        node, 
        view_id, 
        in_tree_view, 
        model_fields,
    ):  
        dict_o_values = {
            'change_default': False,
            'company_dependent': False,
            'context': {},
            'depends': (),
            'domain': [],
            'manual': False,
            'readonly': False,
            'required': False,
            'searchable': False,
            'sortable': False,
            'store': False,
        }
        if model == 'base.merge.wizard' and model_fields:
            active_model = self.env.context.get('active_model') or 'ir.model'
            model_fields['target_id'] = dict_o_values.copy()
            model_fields['target_id']['relation']  = active_model
            model_fields['target_id']['type']  = 'many2one'
            model_fields['target_id']['string']  = 'Target model'
            model_fields['source_ids'] = dict_o_values.copy()
            model_fields['source_ids']['relation']  = active_model
            model_fields['source_ids']['type'] = 'many2many'
            model_fields['source_ids']['string'] = 'Target model records'
        result = super(View, self).postprocess(
            model=model,
            node=node,
            view_id=view_id,
            in_tree_view=in_tree_view,
            model_fields=model_fields)
        return result
