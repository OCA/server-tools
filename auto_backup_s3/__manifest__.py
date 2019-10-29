{
    'name': "Database Auto-Backup to Amazon S3",
    'version': '12.0.1.0.0',
    "category": "Tools",
    "author":
        "Andrii Semko, "
        "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools/",
    'depends': ['base'],
    'data': [
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'views/s3_backup_views.xml',
    ],
    'auto_install': False,
    'installable': True,
}
