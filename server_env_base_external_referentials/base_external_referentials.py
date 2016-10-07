# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2012 Camptocamp SA
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

from osv import fields, models
from server_environment import serv_config
import logging



class external_referential(models.Model):
    _inherit = 'external.referential'

    def _get_environment_config_by_name(self, cr, uid, ids, field_names, arg, context):
        values = {}
        for referential in self.browse(cr, uid, ids, context):
            values[referential.id] = {}
            for field_name in field_names:
                section_name = '.'.join((self._name.replace('.', '_'), referential.name))
                try:
                    value = serv_config.get(section_name, field_name)
                    values[referential.id].update({field_name: value})
                except:
                    logger = logging.getLogger(__name__)
                    logger.exception('error trying to read field %s in section %s', field_name, section_name)
        return values

    _columns = {
        'location': fields.function(_get_environment_config_by_name, type='char', size=200,
                    method=True, string='Location', multi='connection_config'),
        'apiusername': fields.function(_get_environment_config_by_name, type='char', size=64,
                       method=True, string='User Name', multi='connection_config'),
        'apipass': fields.function(_get_environment_config_by_name, type='char', size=64,
                   method=True, string='Password', multi='connection_config'),
    }

external_referential()
