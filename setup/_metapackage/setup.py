import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-server-tools",
    description="Meta package for oca-server-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-base_cron_exclusion',
        'odoo13-addon-base_jsonify',
        'odoo13-addon-company_country',
        'odoo13-addon-onchange_helper',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
