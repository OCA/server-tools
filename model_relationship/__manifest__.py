{
    "name": "Model Relationship",
    "version": "17.0.1.0.0",
    "author": "HomebrewSoft",
    "website": "https://github.com/OCA/server-tools",
    "license": "LGPL-3",
    "depends": [],
    "data": [
        # security
        "security/ir.model.access.csv",
        # data
        # reports
        # views
        "wizards/model_rel_wizard.xml",
    ],
    "external_dependencies": {
        "python": [
            "graphviz",
        ],
    },
    "maintainers": ["AfroMonkey"],
    "development_status": "Beta",
}
