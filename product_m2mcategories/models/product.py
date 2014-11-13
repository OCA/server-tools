##########################################################################
#  Copyright (C) 2009  Sharoon Thomas & Open ERP Community               #
#                                                                        #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
##########################################################################
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    categ_id = fields.Many2one(string='Pricing/Primary Category')
    categ_ids = fields.Many2many(
        comodel_name='product.category', relation='product_categ_rel',
        column1='product_id', column2='categ_id', string='Product Categories')
