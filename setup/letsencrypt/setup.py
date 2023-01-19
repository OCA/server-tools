import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'external_dependencies_override': {
            'python': {
                'acme': 'acme',
                'cryptography': 'cryptography',
                'dns': 'dnspython==1.16.0',
                'josepy': 'josepy',
            }
        }
    },
)
