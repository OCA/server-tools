# coding: utf-8
##############################################################################
#
#    Copyright (C) 2015-TODAY Akretion (<http://www.akretion.com>).
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

from openerp import models, api, _
from openerp.exceptions import Warning as UserError
from openerp.modules import get_module_path

# https://github.com/jdunck/python-unicodecsv
import unicodecsv
try:
    from cStringIO import StringIO
except:
    import StringIO
import logging
import os

_logger = logging.getLogger(__name__)

FILENAME = 'ir.model.access2.csv'

CSV_COLUMN = ['id', 'name', 'model:id', 'group_id:id',
              'perm_read', 'perm_write', 'perm_create', 'perm_unlink']

# TODO: not only create file, add update
# TODO debug concrete models inherit abstract model


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.one
    def button_save_security(self):
        models = self.search_unaccess_models()
        if models:
            csv_file = StringIO()
            writer = unicodecsv.writer(csv_file, encoding='utf-8')
            writer.writerow(CSV_COLUMN)
            self.add_missing_models(models, writer)
            security_path = os.path.join(
                get_module_path(self.name), 'security')
            try:
                self.update_file(csv_file, security_path)
            except:
                raise UserError(
                    _("Impossible to update/create the file in this path '%s'")
                    % security_path)
        # TODO return info to the user
        return True

    @api.model
    def add_missing_models(self, models, writer):
        for model in models:
            print model
            meta = {
                'model_w_underscore': model.model.replace('.', '_'),
                'model_w_space': model.model.replace('.', ' '),
                'module': self.name,
            }
            struct = {
                # TODO 'base' by xmlid  of the group
                'id': 'access_%(model_w_underscore)s_base' % meta,
                'name': "access '%(model_w_space)s' base" % meta,
                'model:id': '%(module)s.model_%(model_w_underscore)s' % meta,
                # TODO replace 'base' by the module which created the group
                'group_id:id': 'base.group_user' % meta,
                'perm_read': 1,
                'perm_write': 0,
                'perm_create': 0,
                'perm_unlink': 0,
            }
            data = []
            for column in CSV_COLUMN:
                data.append(struct[column])
            writer.writerow(data)
        return True

    @api.model
    def search_unaccess_models(self):
        module_path = get_module_path(self.name)
        print module_path
        classes_in_module = self.__metaclass__.module_to_models[self.name]
        all_classes_created_by_the_module = (
            [x for x in classes_in_module
             # classes with _name attribute but not _inherit are required
             if x._name and not hasattr(x, '_inherit')])
        print 'all_classes_created_by_the_module', all_classes_created_by_the_module
        model_names_security_required = (
            [x._name for x in all_classes_created_by_the_module
             # wizard classes shouldn't be include
             if not x._transient and (
                 # only concrete models 'Model' must be include
                 # not 'AbstractModel'
                 x._auto or x._table)])
        print 'model_names_security_required', model_names_security_required
        models = self.env['ir.model'].search(
            [('model', 'in', model_names_security_required)])
        print models
        print [x.model for x in models]
        return models

    @api.model
    def update_file(self, csv_file, security_path):
        if not os.path.isdir(security_path):
            os.mkdir(security_path)
        path = os.path.join(security_path, FILENAME)
        with open(path, 'w') as buf:
            csv_file.seek(0)
            buf.write(csv_file.read())
        _logger.info(
            "\n     -> Security file '%s' saved on the file system" % path)
        # TODO display an alert to the user
        return True
