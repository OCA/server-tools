# -*- coding: utf-8 -*-
"""
Post-Installation Hook for Dependency Map View

This module contains the post-installation hook that automatically adds the
'dependency_map' view mode to all existing window actions in the system.

The hook ensures that the dependency map view is available across all models
without requiring manual configuration for each action.
"""


def post_init_hook(env):
    """
    Add dependency_map view mode to all existing window actions.
    
    This function is executed automatically after the module is installed.
    It searches for all ir.actions.act_window records that have a view_mode
    defined and appends 'dependency_map' to the view_mode if it's not already
    present.
    
    This allows users to access the dependency map view for any model without
    needing to manually update each action's view_mode configuration.
    
    Args:
        env (odoo.api.Environment): The Odoo environment object providing
            access to the database and models.
    
    Returns:
        None
    
    Example:
        After installation, an action with view_mode='tree,form' will be
        updated to view_mode='tree,form,dependency_map'
    
    Note:
        - Only actions with existing view_mode values are modified
        - Duplicate 'dependency_map' entries are prevented by checking first
        - This hook runs once during module installation
    """
    # Search for all window actions that have a view_mode defined
    actions = env['ir.actions.act_window'].search([('view_mode', '!=', False)])
    
    # Iterate through each action and add dependency_map view if not present
    for action in actions:
        # Check if dependency_map is not already in the view_mode
        if 'dependency_map' not in action.view_mode:
            # Append dependency_map to the existing view modes
            action.view_mode = action.view_mode + ',dependency_map'
