# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import socket

{
    "name": "Repetition Rules",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Hidden/Dependency",
    "summary": "Provides a field and widget for RRules according to RFC 2445",
    "depends": [
        'web',
    ],
    "data": [
        'views/templates.xml',
    ],
    "demo": [] if not socket.getfqdn().endswith('odoo-community.org')
    else [
        'demo/res_partner.xml'
    ],
    "qweb": [
        'static/src/xml/field_rrule.xml',
    ],
}
