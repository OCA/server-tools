# coding: utf-8
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'file_email',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """Abstract module for importing and processing the
    attachment of an email. The attachment of the email will be imported
    as a attachment_metadata and then in your custom module you can process it.
    An example of processing can be found in account_statement_email
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['external_file_location', 'fetchmail'],
    'init_xml': [],
    'update_xml': [
        "fetchmail_view.xml",
        "attachment_metadata_view.xml",
        ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
