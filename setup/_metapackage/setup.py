import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-server-tools",
    description="Meta package for oca-server-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-base_jsonify',
        'odoo12-addon-base_search_fuzzy',
        'odoo12-addon-datetime_formatter',
        'odoo12-addon-excel_import_export',
        'odoo12-addon-excel_import_export_demo',
        'odoo12-addon-html_image_url_extractor',
        'odoo12-addon-html_text',
        'odoo12-addon-module_auto_update',
        'odoo12-addon-scheduler_error_mailer',
        'odoo12-addon-sentry',
        'odoo12-addon-sql_request_abstract',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
