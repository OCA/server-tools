{
    "name": "Base Kanban Stage",
    "summary": "Provides stage model and abstract logic for DMM",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/base_kanban_stage.xml",
        "views/base_kanban_abstract.xml",
        "views/ir_model_views.xml",
    ],
    "installable": True,
}
