import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-server-tools",
    description="Meta package for oca-server-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-auditlog',
        'odoo12-addon-auto_backup',
        'odoo12-addon-base_cron_exclusion',
        'odoo12-addon-base_exception',
        'odoo12-addon-base_fontawesome',
        'odoo12-addon-base_jsonify',
        'odoo12-addon-base_search_fuzzy',
        'odoo12-addon-base_technical_user',
        'odoo12-addon-database_cleanup',
        'odoo12-addon-datetime_formatter',
        'odoo12-addon-dbfilter_from_header',
        'odoo12-addon-excel_import_export',
        'odoo12-addon-excel_import_export_demo',
        'odoo12-addon-fetchmail_notify_error_to_sender',
        'odoo12-addon-html_image_url_extractor',
        'odoo12-addon-html_text',
        'odoo12-addon-module_analysis',
        'odoo12-addon-module_auto_update',
        'odoo12-addon-onchange_helper',
        'odoo12-addon-scheduler_error_mailer',
        'odoo12-addon-sentry',
        'odoo12-addon-sql_export',
        'odoo12-addon-sql_request_abstract',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
