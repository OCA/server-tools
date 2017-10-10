#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# closure.py
# ---------------------------------------------------------------------
# Copyright (c) 2016, 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-07-13

'''Find a topologically ordered set of record relations.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import logging
from openerp import fields
from openerp.models import MAGIC_COLUMNS

_logger = logging.getLogger(__name__)


FIELD_RELATED = (fields.One2many, fields.Many2one, fields.Many2many)
NON_CLOSURE_COLUMNS = MAGIC_COLUMNS + [
    'message_ids', 'rml_footer', 'rml_header',
    'rml_paper_format', 'rml_footer_readonly',
    'rml_header2', 'rml_header3', 'rml_header1', 'duration'
]
EXCLUDE_MODELS = ('report.paperformat', 'res.currency.rate',
                  'account.journal.cashbox.line')


def find_closure(records, max_steps=4):
    '''Find the closure from `records`.

    We walk along the relations starting from `records` and traverse up to
    `max_steps` away.  We don't repeat any record.


    '''
    def get_related(records, depth):
        objects = set()
        if depth:
            for record in records:
                if record._name not in EXCLUDE_MODELS:
                    for name, field in record._fields.items():
                        if name not in NON_CLOSURE_COLUMNS and field.store \
                           and isinstance(field, FIELD_RELATED):
                            res = getattr(record, name, None)
                            if res:
                                for related in get_related(res, depth - 1):
                                    objects.add(related)
                    objects.add(record)
        return list(objects)

    from xoutil.functools import partial, lru_cache
    bail_with_zero = partial(bail, default=0)
    res = get_related(records, max_steps)

    def filter_record_with_xml_id(r):
        xml_ids = r._get_xml_ids()[r.id]
        for i in xml_ids:
            if 'mail_threads' not in i and 'export' not in i:
                return False
        return True

    res_filtered = filter(filter_record_with_xml_id, res)
    nodes = [InstanceNode(r) for r in res_filtered]
    nodes_sorted = topological_sort(nodes, lru_cache(100), bail_with_zero)
    return [node.record for node in nodes_sorted]


class InstanceNode(object):
    '''A node that represents a singletong Odoo recordset.

    '''
    def __init__(self, record, coming_from=None):
        record.ensure_one()
        self.record = record
        self.name = record.name_get()
        self.model = record.browse()
        self.coming_from = coming_from   # Just for pretty printing

    def __str__(self):
        if self.coming_from:
            return '%s (from: %s)' % (self.name, self.coming_from)
        else:
            return '%s' % self.name

    def __repr__(self):
        return '<%s>' % self

    def __eq__(self, other):
        if isinstance(other, InstanceNode):
            return self.record == other.record
        else:
            raise TypeError(
                'Incomparable types InstanceNode and %s' % type(other)
            )

    def __hash__(self):
        return hash((self.record._name, self.record.id))

    @property
    def depends(self):
        Many2One = fields.Many2one

        def _gen():
            for name, field in self.model._fields.items():
                # Bail for standard non-interesting fields
                if name not in MAGIC_COLUMNS and isinstance(field, Many2One):
                    res = getattr(self.record, name, None)
                    if res:
                        yield InstanceNode(res, coming_from=name)

        from xoutil.iterators import delete_duplicates as without_duplicates
        return without_duplicates(list(_gen()))

    def closure(self, max_steps=4):
        '''Finds the closure of the graph.

        '''
        pass


def topological_sort(nodes, *optimizations):
    '''Return a topological sort of `nodes`.

    :param nodes: An list of nodes.  See the interface `Node`:class:.

    If a topological sort is not possible (i.e there are cycles ``a < b <
    a``), raise a RuntimeError.


    .. rubric:: Algorithm

    We assign a score to each node.  The score of a node is 0 if and only if
    the node has no dependencies; otherwise the score of a node is defined as
    the maximum score of its dependencies plus one.  Thus, the topological
    order is obtained simply by arranging the nodes w.r.t their score.

    .. rubric:: Internal API and optimizations

    :arg optimizations: A list of decorators for the score function.

    Optimizations allow to adapt the recursive function score to suit your
    needs.  For instance, cycle detection is actually implement by letting the
    score function reach the maximum recursion depth.  If you call this
    function many times, faster cycle detection could be a win.

    Another possible optimization is to cache the result of the scoring
    function.  If your graph is large and with many edges, this could also
    improve performance.

    Ultimately, you may entirely replace the score function for another
    implementation.

    '''
    if optimizations:
        from xoutil.functools import compose
        optimize = compose(*optimizations)
    else:
        optimize = lambda x: x  # noqa

    @optimize
    def score(node):
        if node.depends:
            result = max(score(dep) for dep in node.depends) + 1
        else:
            result = 0
        return result

    return list(sorted(nodes, key=score))


# Optimizations to the `topological_sort` algorithm.
def raise_on_cycle(func):
    '''Make `func` to raise on the first recursive call with the same
    argument.

    '''
    stack = []

    def inner(node):
        if node in stack:
            raise RuntimeError(
                'Cycle detected: %r' % [n for n in stack + [node]]
            )
        else:
            stack.append(node)
            try:
                return func(node)
            finally:
                stack.pop(-1)
    return inner


def bail(func, default=None):
    '''Make `func` bail on the first recursive call with the same argument.

    '''
    stack = []

    def inner(node):
        if node in stack:
            _logger.warn('Ignoring cycle detected: %r',
                         [n for n in stack + [node]])
            return default
        else:
            stack.append(node)
            try:
                return func(node)
            finally:
                stack.pop(-1)
    return inner
