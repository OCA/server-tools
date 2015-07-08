# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.web.controllers import main
from openerp.tools.safe_eval import safe_eval
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
import base64


class actions_server(orm.Model):
    _inherit = "ir.actions.server"

    def __init__(self, pool, cr):
        super(actions_server, self).__init__(pool, cr)
        # add state 'export_email'
        new_state = ('export_email', _('Export data by email'))
        if new_state not in self._columns['state'].selection:
            self._columns['state'].selection.append(new_state)
        return

    _columns = {
        'model': fields.related('model_id', 'model',
                                type="char", size=256, string='Model'),
        'filter_id': fields.many2one(
            'ir.filters', string='Filter', ondelete='restrict'),
        'email_template_id': fields.many2one(
            'email.template', string='Template', ondelete='restrict'),
        'saved_export_id': fields.many2one(
            'ir.exports', string='Saved export', ondelete='restrict'),
        'fields_to_export': fields.text(
            'Fields to export',
            help="The list of fields to export. \
                          The format is ['name', 'seller_ids/product_name']"),
        'export_format': fields.selection([('csv', 'CSV'),
                                           ('xls', 'Excel')],
                                          'Export Formats'),
    }

    def _get_email_template(self, cr, uid, context=None):
        email_template_id = 0
        try:
            model_data_obj = self.pool['ir.model.data']
            email_template_id = model_data_obj.get_object_reference(
                cr, uid, 'base_export_email', 'export_data_email_template')[1]
        except ValueError:
            pass
        return email_template_id

    _defaults = {
        'fields_to_export': '[]',
        'export_format': 'csv',
        'email_template_id': lambda self, cr, uid, c:
        self._get_email_template(cr, uid, context=c),
    }

    def onchange_model_id(self, cr, uid, ids, model_id, context=None):
        """
        Used to set correct domain on filter_id and saved_export_id
        """
        data = {'model': False,
                'filter_id': False,
                'saved_export_id': False}
        if model_id:
            model = self.pool['ir.model'].browse(cr, uid, model_id,
                                                 context=context)
            data.update({'model': model.model})
        return {'value': data}

    def _search_data(self, cr, uid, action, context=None):
        obj_pool = self.pool[action.model]
        domain = action.filter_id and safe_eval(
            action.filter_id.domain, {'time': time,
                                      'datetime': datetime,
                                      'relativedelta': relativedelta,
                                      }) or []
        ctx = action.filter_id and safe_eval(
            action.filter_id.context) or context
        return obj_pool.search(cr, uid, domain,
                               offset=0, limit=False, order=False,
                               context=ctx)

    def _export_data(self, cr, uid, obj_ids, action, context=None):
        obj_pool = self.pool[action.model]
        export_fields = []
        if action.fields_to_export:
            export_fields = safe_eval(action.fields_to_export)
        if action.saved_export_id:
            # retrieve fields of the selected list
            export_fields.extend(
                [efl.name for efl in
                 action.saved_export_id.export_fields])
        return export_fields, obj_pool.export_data(
            cr, uid, obj_ids, export_fields,
            context=context).get('datas', [])

    def _send_data_email(self, cr, uid, action, export_fields, export_data,
                         context=None):
        """
        Prepare the exported data to send with the template
        of the configuration
        """
        if action.export_format == 'csv':
            export = main.CSVExport()
        else:
            export = main.ExcelExport()
        filename = export.filename(action.model)
        content = export.from_data(export_fields, export_data)

        return self._send_email(cr, uid, action, filename, content,
                                context=context)

    def _send_email(self, cr, uid, action, filename, content,
                    context=None):
        """
        Prepare a message with the exported data to send with the
        template of the configuration
        """
        mail_compose = self.pool['mail.compose.message']
        values = mail_compose.onchange_template_id(
            cr, uid, 0, action.email_template_id, 'comment',
            'ir.actions.server', action.id, context=context)['value']
        values['partner_ids'] = [
            (4, partner_id) for partner_id in values.pop('partner_ids',
                                                         [])
        ]
        if context and context.get('encoded_base_64'):
            data = content
        else:
            if isinstance(content, unicode):
                content = content.encode('utf-8')
            data = base64.b64encode(str(content))
        data_attach = {
            'name': filename,
            'datas': data,
            'datas_fname': filename,
            'description': filename,
        }

        values['attachment_ids'] = [(0, 0, data_attach)]
        compose_id = mail_compose.create(
            cr, uid, values, context=context)
        return mail_compose.send_mail(cr, uid, [compose_id], context=context)

    def run(self, cr, uid, ids, context=None):
        """
        If the state of an action is export_email,
        export data related to the configuration and send the result by email
        """
        for action in self.browse(cr, uid, ids, context):
            if action.state == 'export_email':
                # search data to export
                obj_ids = self._search_data(cr, uid, action, context=context)
                # export data
                export_fields, export_data = self._export_data(
                    cr, uid, obj_ids, action, context=context)
                # Prepare a message with the exported data to send with the
                # template of the configuration
                self._send_data_email(
                    cr, uid, action, export_fields, export_data,
                    context=context)
        return super(actions_server, self).run(cr, uid, ids, context=context)
