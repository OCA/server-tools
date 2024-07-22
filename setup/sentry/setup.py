import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'external_dependencies_override': {
            'python': {
                'sentry_sdk': 'sentry_sdk>=1.17.0,<2',
            }
        }
    },
)
