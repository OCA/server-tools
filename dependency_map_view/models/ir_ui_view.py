# -*- coding: utf-8 -*-
"""
UI View Extension for Dependency Map View Type

This module extends the ir.ui.view model to add 'dependency_map' as a new
view type in Odoo. It enables the system to recognize and handle dependency
map views, and automatically creates default views when needed.

The extension allows any model to have a dependency map view without requiring
manual view definition in XML. If a dependency_map view is requested but doesn't
exist, it will be automatically generated.


"""

from odoo import fields, models, api


class View(models.Model):
    """
    Extension of ir.ui.view to support dependency_map view type.
    
    This class extends Odoo's view model to register 'dependency_map' as a
    valid view type alongside standard views (tree, form, kanban, etc.).
    It also provides automatic view creation functionality when a dependency
    map view is requested but doesn't exist.
    
    Attributes:
        _inherit (str): Inherits from 'ir.ui.view' model
        type (fields.Selection): Extended selection field to include dependency_map
    """
    
    _inherit = 'ir.ui.view'

    # Extend the type selection field to include 'dependency_map' as a valid view type
    type = fields.Selection(
        selection_add=[('dependency_map', 'Dependency Map')],
        ondelete={'dependency_map': 'cascade'}  # Delete views when view type is removed
    )

    @api.model
    def default_view(self, model, view_type):
        """
        Auto-create dependency_map view if it doesn't exist for a model.
        
        This method overrides the default_view method to provide automatic
        view creation for dependency_map views. When a dependency_map view
        is requested for a model but doesn't exist, this method creates a
        minimal default view automatically.
        
        This eliminates the need to manually define dependency_map views in
        XML for every model, as the view will be generated on-demand with
        a standard structure.
        
        Args:
            model (str): The technical name of the model (e.g., 'res.partner')
            view_type (str): The type of view being requested (e.g., 'form',
                'tree', 'dependency_map')
        
        Returns:
            int: The database ID of the view record (either existing or newly created)
        
        Example:
            When requesting dependency_map view for 'sale.order':
            - If view exists: Returns existing view ID
            - If view doesn't exist: Creates new view with minimal arch and returns its ID
        
        Note:
            - Only handles 'dependency_map' view type; other types are passed to parent
            - Created views have a standardized naming convention: {model}.dependency.map.auto
            - The arch is minimal: '<dependency_map/>' as the frontend handles rendering
            - Views are created with 'primary' mode to be used as default
        """
        # Check if the requested view type is dependency_map
        if view_type == 'dependency_map':
            # Search for existing dependency_map view for this model
            view = self.search([
                ('model', '=', model),
                ('type', '=', 'dependency_map')
            ], limit=1)

            # If no view exists, create a default one automatically
            if not view:
                view = self.create({
                    'name': f'{model}.dependency.map.auto',  # Auto-generated name
                    'model': model,  # Target model
                    'type': 'dependency_map',  # View type
                    'arch': '<dependency_map/>',  # Minimal XML architecture
                    'mode': 'primary',  # Set as primary view for this type
                })
            
            # Return the view ID (either found or created)
            return view.id

        # For all other view types, use the standard parent method
        return super().default_view(model, view_type)

    def _get_view_info(self):
        # Get the original dictionary
        view_info = super()._get_view_info()

        view_info['dependency_map'] = {
            'icon': 'fa fa-code-fork',
            'multi_record': True,
        }

        return view_info
