import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-server-tools",
    description="Meta package for oca-server-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-auditlog>=16.0dev,<16.1dev',
        'odoo-addon-base_exception>=16.0dev,<16.1dev',
        'odoo-addon-base_fontawesome>=16.0dev,<16.1dev',
        'odoo-addon-base_m2m_custom_field>=16.0dev,<16.1dev',
        'odoo-addon-base_view_inheritance_extension>=16.0dev,<16.1dev',
        'odoo-addon-dbfilter_from_header>=16.0dev,<16.1dev',
        'odoo-addon-iap_alternative_provider>=16.0dev,<16.1dev',
        'odoo-addon-module_change_auto_install>=16.0dev,<16.1dev',
        'odoo-addon-upgrade_analysis>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
