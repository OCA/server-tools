# -*- coding: utf-8 -*-
"""
Models Package Initialization

This package contains model extensions that add dependency map view
functionality to Odoo's core models.

Modules:
    - ir_ui_view: Extends ir.ui.view to add 'dependency_map' as a new view type
    - ir_actions: Extends ir.actions.act_window to automatically add dependency
                  map view to actions for models with relational fields


"""

# Import view model extension
from . import ir_ui_view

# Import action model extension
from . import ir_actions
