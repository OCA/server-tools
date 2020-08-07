# coding: utf-8
# Copyright 2020 Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from odoo import api, models, SUPERUSER_ID
from odoo.exceptions import AccessDenied
from threading import current_thread
from odoo.tools.cache import ormcache

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def write(self, vals):
        """ Invalidate the cache when some users' groups are modified """
        if 'groups_id' in vals:
            self.env['ip.access.rule']._clear_caches()
        return super(ResUsers, self).write(vals)

    @classmethod
    @ormcache('uid', 'address')
    def _check_ip_access_with_address(cls, uid, address):
        """ If there are one or more rules for the user's groups, validate
        the remote address against them. """
        with cls.pool.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            user = env['res.users'].browse(uid)
            rules = env['ip.access.rule'].sudo().search(
                ['|', '&', ('group_id', '=', False), ('user_id', '=', False),
                 '|', ('group_id', 'in', user.groups_id.ids),
                 ('user_id', '=', uid)])
            if not rules:
                return True
            for rule in rules:
                if rule.match(address):
                    return True
        return False

    @classmethod
    def _check_ip_access(cls, uid):
        """ Wrapper around the ormcache'd method that does the actual check
        """
        try:
            remote_addr = current_thread().environ["REMOTE_ADDR"]
        except (KeyError, AttributeError):
            return True
        if not remote_addr:
            return True
        if not cls._check_ip_access_with_address(uid, remote_addr):
            _logger.warn('Access denied to res.users#%s from IP %s',
                         uid, remote_addr)
            raise AccessDenied()
        return True

    @api.model
    def check_credentials(self, password):
        """ Enforce the IP access policies when the user credentials are
        checked. """
        res = super(ResUsers, self).check_credentials(password)
        self._check_ip_access(self.id)
        return res
