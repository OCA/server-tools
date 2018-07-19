# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import api, exceptions, models, tools, _


_logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    @tools.ormcache_context(
        'self._uid', 'self._name', 'operation', 'raise_exception',
        keys=('lang',))
    def _check_access_restriction(self, operation, raise_exception=True):
        """
        Check access restriction for current model.
        If the user is a super user, access restriction are bypassed.
        Models starting with 'ir.' are also bypassed.
        :param operation: str
        :param raise_exception: bool
        :return: bool
        """
        user = self.env.user
        if (user and user._is_superuser()) or self._name.startswith('ir.'):
            return True
        if operation not in ['read', 'write', 'create', 'unlink']:
            raise exceptions.AccessError(_("Invalid operation!"))
        permission = 'perm_%s' % operation
        domain = [
            ('model_name', '=', self._name),
            (permission, '=', True),
            ('active', '=', True),
        ]
        # Do in sudo to avoid infinite loop
        # The other solution is to do that in SQL
        # (like into standard check_access_rights() function)
        access_restrictions = self.env['access.restriction'].sudo().search(
            domain)
        if not access_restrictions:
            return True
        allowed_users = access_restrictions.mapped("res_group_ids.users")
        allowed = False
        if user.id in allowed_users.ids:
            allowed = True
        elif raise_exception:
            _logger.info('Access Denied for operation: %s, uid: %s, '
                         'model: %s', operation, self.env.uid, self._name)
            raise exceptions.AccessError(_(
                "Access denied.\nPlease contact your administrator or check "
                "your access restriction rules."))
        return allowed

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """
        During the access rights check, check first if the user can do the
        operation on the current model.
        :param operation: str
        :param raise_exception: bool
        :return: bool
        """
        result = super(Base, self).check_access_rights(
            operation=operation, raise_exception=raise_exception)
        if result:
            allowed = self._check_access_restriction(
                operation, raise_exception=raise_exception)
        else:
            allowed = False
        if not result or not allowed:
            return False
        return result
