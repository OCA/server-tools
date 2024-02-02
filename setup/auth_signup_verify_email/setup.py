import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'external_dependencies_override': {
            'python': {
                'email_validator': 'email_validator<=1.2.1',
            },
        }
    },
)
