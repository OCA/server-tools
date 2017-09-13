# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <http://therp.nl>
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

import inspect
from werkzeug.local import Local
from openerp.sql_db import Cursor
from openerp.modules import module
from openerp.modules.graph import Graph

original = module.load_information_from_description_file
local = Local()
local.rdepends_to_process = {}


def load_information_from_description_file(module, mod_path=None):
    result = original(module, mod_path=mod_path)

    # add the keys you want to react on here
    if result.get('depends_if_installed'):
        cr = _get_cr()
        if cr:
            _handle_depends_if_installed(cr, result)
    if result.get('rdepends_if_installed'):
        cr = _get_cr()
        if cr:
            _handle_rdepends_if_installed(cr, result, module)

    # Apply depends specified in other modules as rdepends
    extra_depends = local.rdepends_to_process.get(module)
    if extra_depends:
        result['depends'] += extra_depends

    return result


def _handle_depends_if_installed(cr, manifest):
    if not manifest.get('depends_if_installed'):
        return

    added_depends = manifest.pop('depends_if_installed')
    added_depends = _installed_modules(cr, added_depends)

    depends = manifest.setdefault('depends', [])
    depends.extend(added_depends)


def _handle_rdepends_if_installed(cr, manifest, current_module):
    graph = _get_graph()
    if not graph:
        return

    rdepends = manifest.pop('rdepends_if_installed')
    rdepends = _installed_modules(cr, rdepends)

    for rdepend in rdepends:
        to_process = local.rdepends_to_process.get(rdepend, set([]))
        local.rdepends_to_process[rdepend] = to_process | set([current_module])
        # If rdepend already in graph, reload it so new depend is applied
        if graph.get(rdepend):
            del graph[rdepend]
            graph.add_module(cr, rdepend)


def _installed_modules(cr, modules):
    if not modules:
        return []

    cr.execute(
        'SELECT name FROM ir_module_module '
        'WHERE state IN %s AND name IN %s',
        (
            tuple(['installed', 'to install', 'to upgrade']),
            tuple(modules),
        ),
    )
    return [module for module, in cr.fetchall()]


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

    # do nothing if we're not installed
    installed = _installed_modules(cr, ['base_manifest_extension'])
    if not installed:
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
    graph.add_modules(cr, to_reload)
