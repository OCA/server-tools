# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields
from openerp.osv.orm import Model
from .. import match_algorithm

class fetchmail_server_folder(Model):
    _name = 'fetchmail.server.folder'
    _rec_name = 'path'

    def _get_match_algorithms(self):
        def get_all_subclasses(cls):
            return cls.__subclasses__() + [subsub 
                    for sub in cls.__subclasses__()
                    for subsub in get_all_subclasses(sub)]
        return dict([(cls.__name__, cls) for cls in get_all_subclasses(
            match_algorithm.base.base)])

    def _get_match_algorithms_sel(self, cr, uid, context=None):
        algorithms=[]
        for cls in self._get_match_algorithms().itervalues():
            algorithms.append((cls.__name__, cls.name))
        return tuple(sorted(algorithms, lambda a, b: cmp(a[0], b[0])))

    _columns = {
            'sequence': fields.integer('Sequence'),
            'path': fields.char(
                'Path', size=256, help='The path to your mail '
                'folder. Typically would be something like \'INBOX.myfolder\'',
                required=True),
            'model_id': fields.many2one('ir.model', 'Model', required=True),
            'model_field': fields.char('Field (model)', size=128),
            'model_order': fields.char('Order (model)', size=128),
            'match_algorithm': fields.selection(
                _get_match_algorithms_sel, 
                'Match algorithm', required=True, translate=True),
            'mail_field': fields.char('Field (email)', size=128),
            'server_id': fields.many2one('fetchmail.server', 'Server'),
            'delete_matching': fields.boolean('Delete matches'),
            'flag_nonmatching': fields.boolean('Flag nonmatching'),
            'match_first': fields.boolean('Use 1st match'),
            'domain': fields.char(
                'Domain', size=128, help='Fill in a search '
                'filter to narrow down objects to match')
            }

    _defaults = {
            'flag_nonmatching': True,
            }

    def get_algorithm(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids, context):
            return self._get_match_algorithms()[this.match_algorithm]()

    def button_attach_mail_manually(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids, context):
            context.update({'default_folder_id': this.id})
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'fetchmail.attach.mail.manually',
                'target': 'new',
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                }

