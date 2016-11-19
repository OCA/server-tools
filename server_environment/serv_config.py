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

import os
import ConfigParser
from lxml import etree
from itertools import chain

from openerp import models, fields
from openerp.tools.config import config as system_base_config

from .system_info import get_server_environment

from openerp.addons import server_environment_files
_dir = os.path.dirname(server_environment_files.__file__)

# Same dict as RawConfigParser._boolean_states
_boolean_states = {'1': True, 'yes': True, 'true': True, 'on': True,
                   '0': False, 'no': False, 'false': False, 'off': False}

if not system_base_config.get('running_env', False):
    raise Exception(
        "The parameter 'running_env' has not be set neither in base config "
        "file option -c or in openerprc.\n"
        "We strongly recommend against using the rc file but instead use an "
        "explicit config file with this content:\n"
        "[options]\nrunning_env = dev"
    )

ck_path = os.path.join(_dir, system_base_config['running_env'])

if not os.path.exists(ck_path):
    raise Exception(
        "Provided server environment does not exist, "
        "please add a folder %s" % ck_path
    )


def setboolean(obj, attr, _bool=None):
    """Replace the attribute with a boolean."""
    if _bool is None:
        _bool = dict(_boolean_states)
    res = _bool[getattr(obj, attr).lower()]
    setattr(obj, attr, res)
    return res


# Borrowed from MarkupSafe
def _escape(s):
    """Convert the characters &<>'" in string s to HTML-safe sequences."""
    return (str(s).replace('&', '&amp;')
                  .replace('>', '&gt;')
                  .replace('<', '&lt;')
                  .replace("'", '&#39;')
                  .replace('"', '&#34;'))


def _listconf(env_path):
    """List configuration files in a folder."""
    files = [os.path.join(env_path, name)
             for name in sorted(os.listdir(env_path))
             if name.endswith('.conf')]
    return files


def _load_config():
    """Load the configuration and return a ConfigParser instance."""
    default = os.path.join(_dir, 'default')
    running_env = os.path.join(_dir,
                               system_base_config['running_env'])
    if os.path.isdir(default):
        conf_files = _listconf(default) + _listconf(running_env)
    else:
        conf_files = _listconf(running_env)

    config_p = ConfigParser.SafeConfigParser()
    # options are case-sensitive
    config_p.optionxform = str
    try:
        config_p.read(conf_files)
    except Exception as e:
        raise Exception('Cannot read config files "%s":  %s' % (conf_files, e))

    return config_p


serv_config = _load_config()


class _Defaults(dict):
    __slots__ = ()

    def __setitem__(self, key, value):
        def func(*a):
            return str(value)
        return dict.__setitem__(self, key, func)


class ServerConfiguration(models.TransientModel):
    """Display server configuration."""
    _name = 'server.config'
    _conf_defaults = _Defaults()

    def __init__(self, pool, cr):
        """Add columns to model dynamically
        and init some properties

        """
        self._add_columns()
        super(ServerConfiguration, self).__init__(pool, cr)
        self.running_env = system_base_config['running_env']
        # Only show passwords in development
        self.show_passwords = self.running_env in ('dev',)
        self._arch = None
        self._build_osv()

    def _format_key(self, section, key):
        return '%s | %s' % (section, key)

    def _add_columns(self):
        """Add columns to model dynamically"""
        cols = chain(
            self._get_base_cols().items(),
            self._get_env_cols().items(),
            self._get_system_cols().items()
        )
        for col, value in cols:
            col_name = col.replace('.', '_')
            setattr(ServerConfiguration,
                    col_name,
                    fields.Char(string=col, readonly=True))
            self._conf_defaults[col_name] = value

    def _get_base_cols(self):
        """ Compute base fields"""
        res = {}
        for col, item in system_base_config.options.items():
            key = self._format_key('openerp', col)
            res[key] = item
        return res

    def _get_env_cols(self, sections=None):
        """ Compute base fields"""
        res = {}
        sections = sections if sections else serv_config.sections()
        for section in sections:
            for col, item in serv_config.items(section):
                key = self._format_key(section, col)
                res[key] = item
        return res

    def _get_system_cols(self):
        """ Compute system fields"""
        res = {}
        for col, item in get_server_environment():
            key = self._format_key('system', col)
            res[key] = item
        return res

    def _group(self, items):
        """Return an XML chunk which represents a group of fields."""
        names = []

        for key in sorted(items):
            names.append(key.replace('.', '_'))
        return ('<group col="2" colspan="4">' +
                ''.join(['<field name="%s" readonly="1"/>' %
                         _escape(name) for name in names]) +
                '</group>')

    def _build_osv(self):
        """Build the view for the current configuration."""
        arch = ('<?xml version="1.0" encoding="utf-8"?>'
                '<form string="Configuration Form">'
                '<notebook colspan="4">')

        # OpenERP server configuration
        rcfile = system_base_config.rcfile
        items = self._get_base_cols()
        arch += '<page string="OpenERP">'
        arch += '<separator string="%s" colspan="4"/>' % _escape(rcfile)
        arch += self._group(items)
        arch += '<separator colspan="4"/></page>'

        arch += '<page string="Environment based configurations">'
        for section in sorted(serv_config.sections()):
            items = self._get_env_cols(sections=[section])
            arch += '<separator string="[%s]" colspan="4"/>' % _escape(section)
            arch += self._group(items)
        arch += '<separator colspan="4"/></page>'

        # System information
        arch += '<page string="System">'
        arch += '<separator string="Server Environment" colspan="4"/>'
        arch += self._group(self._get_system_cols())
        arch += '<separator colspan="4"/></page>'

        arch += '</notebook></form>'
        self._arch = etree.fromstring(arch)

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """Overwrite the default method to render the custom view."""
        res = super(ServerConfiguration, self).fields_view_get(cr, uid,
                                                               view_id,
                                                               view_type,
                                                               context,
                                                               toolbar)
        if view_type == 'form':
            arch_node = self._arch
            xarch, xfields = self._view_look_dom_arch(cr, uid,
                                                      arch_node,
                                                      view_id,
                                                      context=context)
            res['arch'] = xarch
            res['fields'] = xfields
        return res

    def default_get(self, cr, uid, fields_list, context=None):
        res = {}
        for key in self._conf_defaults:
            if 'passw' in key and not self.show_passwords:
                res[key] = '**********'
            else:
                res[key] = self._conf_defaults[key]()
        return res
