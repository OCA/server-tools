{
    'name': 'Dependency & Impact Map View',
    'version': '18.0.1.0.0',
    'summary': 'Interactive visual graph view for analyzing record dependencies and relationships',
    'description': """
        Dependency & Impact Map View
        =============================

        Features:
        ---------
        * Visual graph representation of record relationships
        * Interactive network diagram with vis.js
        * Support for Many2One, One2Many, and Many2Many relationships
        * Color-coded relationship types
        * Hierarchical layout with automatic positioning
        * Click-to-navigate to related records
        * Export capabilities (PNG, JSON, PDF)
        * Real-time relationship analysis
        * Automatic view integration for all models

        Technical:
        ----------
        * Built with OWL framework
        * Responsive design
        * Optimized for large datasets
        * Background PDF generation
        * Progress tracking in systray
    """,
    'category': 'Productivity/Tools',
    'author': 'Faizan Lodhi',
    'website': 'https://github.com/OCA/server-tools',
    'depends': ['base', 'web'],
    'data': [
        'views/default_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dependency_map_view/static/src/libs/vis-network.min.js',
            'dependency_map_view/static/src/components/map_view/map_view.js',
            'dependency_map_view/static/src/components/map_view/map_view.xml',
            'dependency_map_view/static/src/components/map_view/map_view.scss',
        ],
    },
    'images': ['static/description/icon.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'price': 0.00,
    'currency': 'USD',
}
