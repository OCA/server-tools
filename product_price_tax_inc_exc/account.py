    # -*- encoding: utf-8 -*-
###############################################################################
#
#   product_price_tax_inc_exc for OpenERP
#   Copyright (C) 2011-TODAY Akretion <http://www.akretion.com>.
#               All Rights Reserved
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields
from openerp.osv.orm import Model

class account_fiscal_position(Model):
    _inherit = 'account.fiscal.position'
    _columns = {
        'price_compatibility': fields.selection([
                    ('tax-inc', 'Tax Inc'),
                    ('tax-exc', 'Tax Exc'),
                    ('both', 'Both'),
                    ], 'Pricelist Compatibility',
                    help=("Choose the kind of pricelist compatible"
                    "with the fiscal position")),
    }

    _defaults = {
        'price_compatibility': 'tax-exc',
    }
