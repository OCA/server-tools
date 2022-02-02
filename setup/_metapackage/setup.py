import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-server-tools",
    description="Meta package for oca-server-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-base_cron_exclusion>=15.0dev,<15.1dev',
        'odoo-addon-fetchmail_incoming_log>=15.0dev,<15.1dev',
        'odoo-addon-html_text>=15.0dev,<15.1dev',
        'odoo-addon-upgrade_analysis>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
