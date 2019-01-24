# Copyright 2015 Anubía, soluciones en la nube,SL (http://www.anubia.es)
# Copyright 2017 Onestein (http://www.onestein.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def load(self, fields, data):
        '''Overriding this method we only allow its execution
        if current user belongs to the group allowed for CSV data import.
        An exception is raised otherwise, and also log the import attempt.
        '''
        current_user = self.env.user
        allowed_group = 'base_import_security_group.group_import_csv'
        allowed_group_id = self.env.ref(
            allowed_group,
            raise_if_not_found=False
        )
        if not allowed_group_id or current_user.has_group(allowed_group):
            res = super().load(fields=fields, data=data)
        else:
            msg = ('User (ID: %s) is not allowed to import data '
                   'in model %s.') % (self.env.uid, self._name)
            _logger.info(msg)
            messages = []
            info = {}
            messages.append(
                dict(info, type='error', message=msg, moreinfo=None))
            res = {'ids': None, 'messages': messages}
        return res
