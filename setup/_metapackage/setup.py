import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-server-tools",
    description="Meta package for oca-server-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-auditlog',
        'odoo13-addon-base_changeset',
        'odoo13-addon-base_cron_exclusion',
        'odoo13-addon-base_exception',
        'odoo13-addon-base_jsonify',
        'odoo13-addon-base_m2m_custom_field',
        'odoo13-addon-base_name_search_multi_lang',
        'odoo13-addon-base_search_fuzzy',
        'odoo13-addon-base_technical_user',
        'odoo13-addon-base_time_window',
        'odoo13-addon-base_view_inheritance_extension',
        'odoo13-addon-company_country',
        'odoo13-addon-fetchmail_incoming_log',
        'odoo13-addon-fetchmail_notify_error_to_sender',
        'odoo13-addon-fetchmail_notify_error_to_sender_test',
        'odoo13-addon-mail_server_relay_disallowed',
        'odoo13-addon-module_auto_update',
        'odoo13-addon-onchange_helper',
        'odoo13-addon-sentry',
        'odoo13-addon-sql_request_abstract',
        'odoo13-addon-test_base_time_window',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
