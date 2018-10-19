import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-server-tools",
    description="Meta package for oca-server-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-auditlog',
        'odoo11-addon-auto_backup',
        'odoo11-addon-base_cron_exclusion',
        'odoo11-addon-base_exception',
        'odoo11-addon-base_fontawesome',
        'odoo11-addon-base_name_search_improved',
        'odoo11-addon-base_remote',
        'odoo11-addon-base_search_fuzzy',
        'odoo11-addon-base_technical_user',
        'odoo11-addon-configuration_helper',
        'odoo11-addon-database_cleanup',
        'odoo11-addon-datetime_formatter',
        'odoo11-addon-dbfilter_from_header',
        'odoo11-addon-fetchmail_notify_error_to_sender',
        'odoo11-addon-html_image_url_extractor',
        'odoo11-addon-html_text',
        'odoo11-addon-letsencrypt',
        'odoo11-addon-module_auto_update',
        'odoo11-addon-onchange_helper',
        'odoo11-addon-record_archiver',
        'odoo11-addon-scheduler_error_mailer',
        'odoo11-addon-sentry',
        'odoo11-addon-sql_request_abstract',
        'odoo11-addon-test_configuration_helper',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
