# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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

import logging

logger = logging.getLogger('upgrade')


def migrate(cr, version):
    logger.info("Migrating product_custom_attributes from version %s", version)
    cr.execute("SELECT count(pp.attribute_set_id), pp.attribute_set_id "
               "FROM product_product pp "
               "INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id "
               "GROUP BY pp.attribute_set_id "
               "HAVING count(pp.id) > 1")
    if cr.rowcount > 0:
        raise Exception('Impossible to migrate: all the variants should have '
                        'the same attribute set.')
