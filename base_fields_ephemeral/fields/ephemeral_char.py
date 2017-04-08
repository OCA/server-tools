# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)


class EphemeralChar(fields.Char):

    column_type = ('bool', 'bool')

    def get_local_name(self, record):
        local_name = '%s.%s' % (record.id, self.name)
        _logger.debug('Local name = "%s"', local_name)
        return local_name

    def get_local(self, record):
        value = request.session.get(
            self.get_local_name(record),
            self.null(record),
        )
        _logger.debug('Env %s', hash(record.env))
        _logger.debug('Get local %s - "%s"', record, value)
        return value

    def set_local(self, record, value, type_=str, force=False):
        _logger.debug('Set Local %s, %s', record, value)
        if value or force:
            request.session[self.get_local_name(record)] = type_(value)
        return self.get_local(record)

    def determine_value(self, record):
        record._cache[self.name] = self.convert_to_cache(
            self.get_local(record),
            record,
            validate=False,
        )
        _logger.debug('Cache %s', record._cache[self])

    def determine_draft_value(self, record):
        record._cache[self.name] = self.convert_to_cache(
            self.get_local(record),
            record,
            validate=False,
        )
        _logger.debug('Draft Cache %s', record._cache[self])

    def convert_to_column(self, value, record):
        _logger.debug('Convert to col %s, %s', value, record)
        self.set_local(record, value)
        return False

    def convert_to_cache(self, value, record, validate=True):
        return self.set_local(record, value)
