import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'external_dependencies_override': {
            'python': {
                "contextvars": "contextvars; python_version < '3.7'",
            }
        },
    },
)
