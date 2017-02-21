# -*- coding: utf-8 -*-
# License and authorship info in:
# __openerp__.py file at the root folder of this module.

from openerp import api
from openerp.models import BaseModel
import logging

_logger = logging.getLogger(__name__)
base_load = BaseModel.load


@api.model
def load_import_optional(self, fields=None, data=None):
    '''Overriding this method we only allow its execution
    if current user belongs to the group allowed for CSV data import.
    An exception is raised otherwise, and also log the import attempt.
    '''
    res = {}
    current_user = self.env['res.users'].browse(self.env.uid)
    allowed_group = 'base_import_security_group.group_import_csv'
    if current_user and current_user.has_group(allowed_group):
        res = base_load(self, fields=fields, data=data)
    else:
        msg = ('User (ID: %s) is not allowed to import data '
               'in model %s.') % (self.env.uid, self._name)
        _logger.error(msg)
        messages = []
        info = {}
        messages.append(dict(info, type='error', message=msg, moreinfo=None))
        res = {'ids': None, 'messages': messages}
    return res

# Monkey patch function
# Because BaseModel _name = None
BaseModel.load = load_import_optional
