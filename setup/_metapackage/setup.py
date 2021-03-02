import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-server-tools",
    description="Meta package for oca-server-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-auditlog',
        'odoo14-addon-base_cron_exclusion',
        'odoo14-addon-base_exception',
        'odoo14-addon-base_jsonify',
        'odoo14-addon-base_m2m_custom_field',
        'odoo14-addon-base_sparse_field_list_support',
        'odoo14-addon-base_technical_user',
        'odoo14-addon-module_auto_update',
        'odoo14-addon-onchange_helper',
        'odoo14-addon-sentry',
        'odoo14-addon-slow_statement_logger',
        'odoo14-addon-sql_request_abstract',
        'odoo14-addon-upgrade_analysis',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
