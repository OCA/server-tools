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
    cr.execute("UPDATE product_template pt "
               "SET attribute_set_id = (SELECT pp.attribute_set_id_copy "
               "                        FROM product_product pp WHERE "
               "                        pp.product_tmpl_id = pt.id "
               "                        LIMIT 1)"
               "WHERE pt.attribute_set_id IS NULL")
    cr.execute('ALTER TABLE product_product DROP COLUMN attribute_set_id')
