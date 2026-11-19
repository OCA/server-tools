# -*- coding: utf-8 -*-
"""
Window Action Extension for Dependency Map View

This module extends the ir.actions.act_window model to automatically add
the dependency_map view mode to newly created actions when the target model
contains relational fields (Many2One, One2Many, or Many2Many).

The extension intelligently detects whether a model would benefit from the
dependency map view by checking for the presence of relational fields, and
excludes system models (ir.* and mail.*) that typically don't need this view.

"""

from odoo import models, api


class IrActionsActWindow(models.Model):
    """
    Extension of ir.actions.act_window to auto-add dependency map view.
    
    This class extends the standard Odoo window action model to automatically
    include the 'dependency_map' view mode for models that have relational
    fields, making the dependency visualization available without manual
    configuration.
    
    Attributes:
        _inherit (str): Inherits from 'ir.actions.act_window' model
    """
    
    _inherit = 'ir.actions.act_window'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create method to auto-add dependency_map view mode.
        
        This method intercepts the creation of new window actions and
        automatically appends 'dependency_map' to the view_mode if:
        1. The action has a view_mode defined
        2. The dependency_map is not already present
        3. The target model is not a system model (ir.* or mail.*)
        4. The target model has at least one relational field
        
        Args:
            vals_list (list): List of dictionaries containing values for
                creating new action records. Each dictionary represents
                one action to be created.
        
        Returns:
            recordset: The newly created ir.actions.act_window records
        
        Example:
            When creating an action for 'res.partner' model:
            Input: {'name': 'Partners', 'res_model': 'res.partner', 
                    'view_mode': 'tree,form'}
            Result: view_mode becomes 'tree,form,dependency_map'
        
        Note:
            - System models (ir.*, mail.*) are excluded to avoid cluttering
              technical views
            - Models without relational fields are skipped as they wouldn't
              benefit from dependency visualization
            - Errors during field checking are silently caught to prevent
              action creation failures
        """
        # Call parent create method to create the actions
        actions = super().create(vals_list)
        
        # Process each newly created action
        for action in actions:
            # Check if action has view_mode and dependency_map is not already present
            if action.view_mode and 'dependency_map' not in action.view_mode:
                # Verify the action has a target model and it's not a system model
                if action.res_model and not action.res_model.startswith(('ir.', 'mail.')):
                    # Check if model has relational fields that would benefit from dependency map
                    try:
                        # Get the model instance
                        model = self.env[action.res_model]
                        
                        # Retrieve all field definitions for the model
                        fields = model.fields_get()
                        
                        # Check if any field is a relational field type
                        has_relations = any(
                            f.get('type') in ['many2one', 'one2many', 'many2many']
                            for f in fields.values()
                        )
                        
                        # If model has relational fields, add dependency_map view
                        if has_relations:
                            action.view_mode = action.view_mode + ',dependency_map'
                    except Exception:
                        # Silently pass if there's any error checking the model
                        # This prevents breaking action creation due to model access issues
                        pass
        
        return actions
