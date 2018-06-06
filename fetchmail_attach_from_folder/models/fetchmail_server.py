# -*- coding: utf-8 -*-
# Copyright - 2013-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import simplejson
from lxml import etree

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import UnquoteEvalContext


_logger = logging.getLogger(__name__)


class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    folder_ids = fields.One2many(
        comodel_name='fetchmail.server.folder',
        inverse_name='server_id',
        string='Folders',
        context={'active_test': False})
    object_id = fields.Many2one(required=False)  # comodel_name='ir.model'
    type = fields.Selection(default='imap')
    folders_only = fields.Boolean(
        string='Only folders, not inbox',
        help="Check this field to leave imap inbox alone"
             " and only retrieve mail from configured folders.")

    @api.onchange('type', 'is_ssl', 'object_id')
    def onchange_server_type(self):
        super(FetchmailServer, self).onchange_server_type()
        self.state = 'draft'

    @api.onchange('folder_ids')
    def onchange_folder_ids(self):
        self.onchange_server_type()

    @api.multi
    def fetch_mail(self):
        for this in self:
            if not this.folders_only:
                super(FetchmailServer, this).fetch_mail()
            try:
                # New connection for retrieving folders
                connection = this.connect()
                for folder in this.folder_ids.filtered('active'):
                    if folder.state == 'done':
                        folder.retrieve_imap_folder(connection)
                connection.close()
            except Exception:
                _logger.error(_(
                    "General failure when trying to connect to"
                    " %s server %s."),
                    this.type, this.name, exc_info=True)
            finally:
                if connection:
                    connection.logout()
        return True

    def fields_view_get(
            self, view_id=None, view_type='form',
            toolbar=False, submenu=False):
        """Set modifiers for form fields in folder_ids depending on algorithm.

        A field will be readonly and/or required if this is specified in the
        algorithm.
        """
        result = super(FetchmailServer, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type == 'form':
            view = etree.fromstring(
                result['fields']['folder_ids']['views']['form']['arch'])
            modifiers = {}
            docstr = ''
            folder_model = self.env['fetchmail.server.folder']
            match_algorithms = folder_model._get_match_algorithms()
            for algorithm in match_algorithms.itervalues():
                for modifier in ['required', 'readonly']:
                    for field in getattr(algorithm, modifier + '_fields'):
                        modifiers.setdefault(field, {})
                        modifiers[field].setdefault(modifier, [])
                        if modifiers[field][modifier]:
                            modifiers[field][modifier].insert(0, '|')
                        modifiers[field][modifier].append(
                            ("match_algorithm", "==", algorithm.__name__))
                docstr += _(algorithm.name) + '\n' + _(algorithm.__doc__) + \
                    '\n\n'
            for field in view.xpath('//field'):
                if field.tag == 'field' and field.get('name') in modifiers:
                    patched_modifiers = field.attrib['modifiers'].replace(
                        'false', 'False').replace('true', 'True')
                    original_dict = safe_eval(
                        patched_modifiers,
                        UnquoteEvalContext({}),
                        nocopy=True)
                    modifier_dict = modifiers[field.attrib['name']]
                    combined_dict = dict(original_dict, **modifier_dict)
                    field.set('modifiers', simplejson.dumps(combined_dict))
                if (field.tag == 'field' and
                        field.get('name') == 'match_algorithm'):
                    field.set('help', docstr)
            result['fields']['folder_ids']['views']['form']['arch'] = \
                etree.tostring(view)
        return result
