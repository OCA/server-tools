# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import inspect
from openerp.sql_db import Cursor
from openerp.modules import module
from openerp.modules.graph import Graph
original = module.load_information_from_description_file


def load_information_from_description_file(module, mod_path=None):
    result = original(module, mod_path=mod_path)
    # add the keys you want to react on here
    if result.get('depends_if_installed'):
        cr = _get_cr()
        if cr:
            _handle_depends_if_installed(cr, result)

    return result


def _handle_depends_if_installed(cr, manifest):
    if not manifest.get('depends_if_installed'):
        return
    cr.execute(
        'select name from ir_module_module '
        'where state in %s and name in %s',
        (
            tuple(['installed', 'to install', 'to upgrade']),
            tuple(manifest['depends_if_installed']),
        ),
    )
    manifest.pop('depends_if_installed')
    depends = manifest.setdefault('depends', [])
    depends.extend(module for module, in cr.fetchall())


def _get_cr():
    cr = None
    for frame, filename, lineno, funcname, line, index in inspect.stack():
        # walk up the stack until we've found a cursor
        if 'cr' in frame.f_locals and isinstance(frame.f_locals['cr'], Cursor):
            cr = frame.f_locals['cr']
            break
    return cr


def _get_graph():
    graph = None
    for frame, filename, lineno, funcname, line, index in inspect.stack():
        # walk up the stack until we've found a graph
        if 'graph' in frame.f_locals and isinstance(
            frame.f_locals['graph'], Graph
        ):
            graph = frame.f_locals['graph']
            break
    return graph


def post_load_hook():
    cr = _get_cr()
    if not cr:
        return
    cr.execute(
        'select id from ir_module_module where name=%s and state in %s',
        (
            'base_manifest_extension',
            tuple(['installed', 'to install', 'to upgrade']),
        ),
    )
    # do nothing if we're not installed
    if not cr.rowcount:
        return

    module.load_information_from_description_file =\
        load_information_from_description_file

    # here stuff can become tricky: On the python level, modules
    # are not loaded in dependency order. This means that there might
    # be modules loaded depending on us before we could patch the function
    # above. So we reload the module graph for all modules coming after us

    graph = _get_graph()
    if not graph:
        return

    this = graph['base_manifest_extension']
    to_reload = []
    for node in graph.itervalues():
        if node.depth > this.depth:
            to_reload.append(node.name)
    for module_name in to_reload:
        del graph[module_name]
        graph.add_module(cr, module_name)
