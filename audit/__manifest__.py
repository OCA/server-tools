# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring,pointless-statement
{
    "name": "Audit",
    "summary": (
        "Generic audit and checklist engine: domains, targets, snapshots, "
        "and team-based access control."
    ),
    "author": "AMV Limited, Odoo Community Association (OCA)",
    "website": "https://vapo.co.nz",
    "category": "Services",
    "version": "19.0.1.0.0",
    "license": "Other proprietary",
    "application": True,
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/actions.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": ["audit/static/src/**/*"],
    },
}
