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
    '''Overriding this method we only allow its execution if the current
    user belongs to the group allowed for CSV data import.
    An exception is raised otherwise, and the import attempt is logged.
    This method is monkeypatched and will also affect other databases on the
    same Odoo instance. Therefore, check if the group actually exist as
    evidence that this module is installed.
    '''
    group_ref = 'base_import_security_group.group_import_csv'
    group = self.env.ref(group_ref, raise_if_not_found=False)
    if not group or self.env.user.has_group(group_ref):
        return base_load(self, fields=fields, data=data)
    msg = 'User (ID: %s) is not allowed to import data in model %s.' % (
        self.env.uid, self._name)
    _logger.info(msg)
    return {'ids': False, 'messages': [{
        'type': 'error',
        'message': msg,
        'moreinfo': False}]}


def post_load():
    BaseModel.load = load_import_optional
