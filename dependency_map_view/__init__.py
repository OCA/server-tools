# -*- coding: utf-8 -*-
"""
Dependency & Impact Map View Module Initialization

This module provides an interactive visual graph view for analyzing record
dependencies and relationships in Odoo. It enables users to visualize how
records are connected through Many2One, One2Many, and Many2Many relationships.

The module automatically integrates with all Odoo models that have relational
fields, providing a new 'dependency_map' view type that can be added to any
window action.

Key Components:
    - models: Contains model extensions for ir.ui.view and ir.actions.act_window
    - hooks: Post-installation hook to add dependency_map view to existing actions

"""

# Import model extensions
from . import models

# Import post-installation hook for automatic view integration
from .hooks import post_init_hook
