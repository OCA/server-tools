# Dependency & Impact Map View

Interactive visual graph view for analyzing record dependencies and relationships in Odoo.

## Features

- **Visual Graph Representation**: Interactive network diagram showing record relationships
- **Multiple Relationship Types**: Support for Many2One, One2Many, and Many2Many fields
- **Color-Coded Relationships**: Different colors for different relationship types
- **Interactive Navigation**: Click on nodes to navigate to related records
- **Hierarchical Layout**: Automatic positioning with vis.js network library
- **Export Capabilities**: Export maps as PNG, JSON, or PDF
- **Real-time Analysis**: Dynamic relationship discovery and visualization
- **Auto-Integration**: Automatically available for all Odoo models

## Installation

1. Copy the module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Dependency & Impact Map View" module

## Usage

1. Go to any model's list view (e.g., Sales Orders, Customers, Products)
2. Click on the view switcher and select "Dependency Map" view
3. The system will automatically generate a visual map of record relationships
4. Click on nodes to navigate to related records
5. Use export options to save the map

## Technical Details

- **Framework**: Built with OWL (Odoo Web Library)
- **Visualization**: Uses vis.js network library
- **Compatibility**: Odoo 18.0+
- **Auto-View Creation**: Automatically creates dependency_map views for any model
- **Performance**: Optimized for large datasets with progressive loading

## Configuration

No configuration required. The module automatically:
- Registers the new view type
- Creates default views for all models
- Integrates with existing Odoo interface

## Author

**Faizan Lodhi**  
Website: https://axiomworld.net

## License

LGPL-3