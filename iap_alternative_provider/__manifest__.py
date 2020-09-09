# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "IAP Alternative Provider",
    "summary": "Base module for providing alternative provider for iap apps",
    "version": "12.0.1.0.0",
    "category": "Tools",
    "website": "http://github.com/OCA/server-tools",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["sebastienbeau"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["iap", "server_environment"],
    "data": ["views/iap_account_view.xml"],
    "demo": [],
    "qweb": [],
}
