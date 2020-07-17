# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Ir Attachment S3",
    "version": "12.0.1.0.0",
    "category": "Tools",
    "website": "https://nodrizatech.com/",
    "author": "Odoo Nodriza Tech (ONT), "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    'external_dependencies': {
        'python3': ['boto3'],
    },
    "depends": [
        "base"
    ],
    "data": [
        "data/ir_cron.xml",
        "data/ir_configparameter_data.xml",
    ],
    "installable": True,
}