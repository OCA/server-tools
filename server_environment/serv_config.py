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
import configparser
from lxml import etree
from itertools import chain

from odoo import api, fields, models
from odoo.tools.config import config as system_base_config

from .system_info import get_server_environment

from odoo.addons import server_environment_files
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

    config_p = configparser.SafeConfigParser()
    # options are case-sensitive
    config_p.optionxform = str
    try:
        config_p.read(conf_files)
    except Exception as e:
        raise Exception('Cannot read config files "%s":  %s' % (conf_files, e))
    config_p.read(system_base_config.rcfile)
    config_p.remove_section('options')

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

    @classmethod
    def _build_model(cls, pool, cr):
        """Add columns to model dynamically
        and init some properties

        """
        ModelClass = super(ServerConfiguration, cls)._build_model(pool, cr)
        ModelClass._add_columns()
        ModelClass.running_env = system_base_config['running_env']
        # Only show passwords in development
        ModelClass.show_passwords = ModelClass.running_env in ('dev',)
        ModelClass._arch = None
        ModelClass._build_osv()
        return ModelClass

    @classmethod
    def _format_key(cls, section, key):
        return '%s | %s' % (section, key)

    @classmethod
    def _add_columns(cls):
        """Add columns to model dynamically"""
        cols = chain(
            list(cls._get_base_cols().items()),
            list(cls._get_env_cols().items()),
            list(cls._get_system_cols().items())
        )
        for col, value in cols:
            col_name = col.replace('.', '_')
            setattr(ServerConfiguration,
                    col_name,
                    fields.Char(string=col, readonly=True))
            cls._conf_defaults[col_name] = value

    @classmethod
    def _get_base_cols(cls):
        """ Compute base fields"""
        res = {}
        for col, item in list(system_base_config.options.items()):
            key = cls._format_key('odoo', col)
            res[key] = item
        return res

    @classmethod
    def _get_env_cols(cls, sections=None):
        """ Compute base fields"""
        res = {}
        sections = sections if sections else serv_config.sections()
        for section in sections:
            for col, item in serv_config.items(section):
                key = cls._format_key(section, col)
                res[key] = item
        return res

    @classmethod
    def _get_system_cols(cls):
        """ Compute system fields"""
        res = {}
        for col, item in get_server_environment():
            key = cls._format_key('system', col)
            res[key] = item
        return res

    @classmethod
    def _group(cls, items):
        """Return an XML chunk which represents a group of fields."""
        names = []

        for key in sorted(items):
            names.append(key.replace('.', '_'))
        return ('<group col="2" colspan="4">' +
                ''.join(['<field name="%s" readonly="1"/>' %
                         _escape(name) for name in names]) +
                '</group>')

    @classmethod
    def _build_osv(cls):
        """Build the view for the current configuration."""
        arch = ('<?xml version="1.0" encoding="utf-8"?>'
                '<form string="Configuration Form">'
                '<notebook colspan="4">')

        # Odoo server configuration
        rcfile = system_base_config.rcfile
        items = cls._get_base_cols()
        arch += '<page string="Odoo">'
        arch += '<separator string="%s" colspan="4"/>' % _escape(rcfile)
        arch += cls._group(items)
        arch += '<separator colspan="4"/></page>'

        arch += '<page string="Environment based configurations">'
        for section in sorted(serv_config.sections()):
            items = cls._get_env_cols(sections=[section])
            arch += '<separator string="[%s]" colspan="4"/>' % _escape(section)
            arch += cls._group(items)
        arch += '<separator colspan="4"/></page>'

        # System information
        arch += '<page string="System">'
        arch += '<separator string="Server Environment" colspan="4"/>'
        arch += cls._group(cls._get_system_cols())
        arch += '<separator colspan="4"/></page>'

        arch += '</notebook></form>'
        cls._arch = etree.fromstring(arch)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Overwrite the default method to render the custom view."""
        res = super(ServerConfiguration, self).fields_view_get(view_id,
                                                               view_type,
                                                               toolbar)
        View = self.env['ir.ui.view']
        if view_type == 'form':
            arch_node = self._arch
            xarch, xfields = View.postprocess_and_fields(
                self._name, arch_node, view_id)
            res['arch'] = xarch
            res['fields'] = xfields
        return res

    @api.model
    def default_get(self, fields_list):
        res = {}
        for key in self._conf_defaults:
            if 'passw' in key and not self.show_passwords:
                res[key] = '**********'
            else:
                res[key] = self._conf_defaults[key]()
        return res
