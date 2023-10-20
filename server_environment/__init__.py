# -*- coding: utf-8 -*-
##############################################################################
#
#    Adapted by Nicolas Bessi. Copyright Camptocamp SA
#    Based on Florent Xicluna original code. Copyright Wingo SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from . import models
# TODO when migrating to 12, fix the import of serv_config by renaming the
# file?
# Add an alias to access to the 'serv_config' module as it is shadowed
# in the following line by an import of a variable with the same name.
# We can't change the import of serv_config for backward compatibility.
from . import serv_config as server_env
from .serv_config import serv_config, setboolean
