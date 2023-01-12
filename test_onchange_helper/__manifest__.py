# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Onchange Helper TEST",
    "summary": """
        Test addon for the onchange_helper addon""",
    "version": "10.0.2.1.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools"
               "/tree/10.0/test_onchange_helper",
    "depends": ["onchange_helper"],
    "data": [
        'security/test_onchange_helper_multi_line.xml',
        'security/test_onchange_helper_multi.xml',
        "security/test_onchange_helper_emailmessage.xml",
        "security/test_onchange_helper_message.xml",
        "security/test_onchange_helper_discussion.xml",
        "security/test_onchange_helper_category.xml",
    ],
    "demo": [
        "demo/test_onchange_helper_discussion.xml",
        "demo/test_onchange_helper_message.xml",
    ]
}
