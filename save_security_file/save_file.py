# -*- coding: utf-8 -*-
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

from openerp import models, api
from openerp.modules import get_module_path


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.one
    def button_save_security(self):
        module_path = get_module_path(self.name)
        print module_path
        classes_in_module = self.__metaclass__.module_to_models[self.name]
        all_models_created_by_the_module = (
            [x for x in classes_in_module
             if x._name and not hasattr(x, '_inherit')])
        print all_models_created_by_the_module
        import pdb; pdb.set_trace()
        return True
