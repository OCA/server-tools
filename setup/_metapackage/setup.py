import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-server-tools",
    description="Meta package for oca-server-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-auditlog',
        'odoo13-addon-base_cron_exclusion',
        'odoo13-addon-base_jsonify',
        'odoo13-addon-base_m2m_custom_field',
        'odoo13-addon-base_search_fuzzy',
        'odoo13-addon-base_time_window',
        'odoo13-addon-company_country',
        'odoo13-addon-onchange_helper',
        'odoo13-addon-test_base_time_window',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
