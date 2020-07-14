# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Slack",
    "version": "12.0.1.0.0",
    "category": "Tools",
    "website": "https://nodrizatech.com/",
    "author": "Odoo Nodriza Tech (ONT), "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "base",
        "sale"
    ],
    "external_dependencies": {
        "python3" : ["slackclient"],
    },
    "data": [
        "data/slack_data.xml",
        "views/res_users_view.xml",
    ],
    "installable": True,
}