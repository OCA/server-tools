# -*- coding: utf-8 -*-
{
    'name': "Store sessions in DB",
    'description': """
    Storing sessions in DB
- workls only with workers > 0
- set the session_db parameter in the odoo config file
- session_db parameter value is a full postgresql connection string, like user:passwd@server/db
- choose another DB than the odoo db itself, for security purpose
- it also possible to use another PostgreSQL user for the same security reasons

Set this module in the server wide modules
    """,
    'category': '',
    'version': '1.0',

    'depends': [
    ],

    'data': [
    ],
    'demo': [
    ],
}
