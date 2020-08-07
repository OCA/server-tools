# coding: utf-8
# Copyright 2020 Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
try:
    import ipaddress
except ImportError:
    ipaddress = None

from threading import current_thread

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.service import wsgi_server


class IpAccessRule(models.Model):
    _name = 'ip.access.rule'
    _description = 'IP Access Rule'

    active = fields.Boolean(default=True)
    group_id = fields.Many2one(
        'res.groups', 'Group', index=True, ondelete='RESTRICT',
        help=(
            'The group to which apply the policy. Keep empty for all groups.'))
    user_id = fields.Many2one(
        'res.users', 'User', index=True, ondelete='RESTRICT',
        help=(
            'Instead of a group, apply the policy only to a specific user.'))
    name = fields.Char('Description')
    network = fields.Char('IP Network or single address to allow logins from')
    private = fields.Boolean('Allow logins from all private addresses')

    @api.constrains('private', 'network')
    def constrain_private_network(self):
        """ Check if both criteria are not enabled simultaneously """
        for ipr in self:
            if ipr.private and ipr.network:
                raise ValidationError(
                    'An access rule cannot have a network setting if the '
                    '`private` toggle is on.')
            if not ipr.private and not ipr.network:
                raise ValidationError(
                    'Please enter a value for `network`, or toggle the '
                    '`private` checkbox')
        return True

    @api.onchange('private')
    def onchange_private(self):
        """ Prevent both criteria from being enabled simultaneously """
        if self.private and self.network:
            self.network = False

    @api.onchange('network')
    def onchange_network(self):
        """ Prevent both criteria from being enabled simultaneously """
        if self.network and self.private:
            self.private = False

    @api.constrains('group_id', 'user_id')
    def constrain_group_user(self):
        """ Check if both selections are not entered simultaneously """
        for ipr in self:
            if ipr.group_id and ipr.user_id:
                raise ValidationError(
                    'An access rule cannot select a group as well as a user')
        return True

    @api.onchange('group_id')
    def onchange_group_id(self):
        if self.group_id and self.user_id:
            self.user_id = False

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id and self.group_id:
            self.group_id = False

    @api.multi
    def match(self, address):
        """ Match `self` against the given address """
        self.ensure_one()
        ip_address = ipaddress.ip_address(unicode(address))
        if self.private:
            return ip_address.is_private
        if self.network:
            return ip_address in ipaddress.ip_network(unicode(self.network))

    @api.model
    def _clear_caches(self):
        """ Clear related caches """
        self.env['res.users']._check_ip_access_with_address.clear_cache(
            self.env['res.users'])

    @api.model
    def create(self, vals):
        """ Clear caches when a new rule is created """
        self._clear_caches()
        return super(IpAccessRule, self).create(vals)

    @api.multi
    def write(self, vals):
        """ Clear caches when a rule is modified, and test the validity of
        the value for `network`. """
        if vals.get('network'):
            try:
                ipaddress.ip_network(vals['network'])
            except Exception as e:
                raise ValidationError(
                    'Invalid IP network %s: %s' % (vals['network'], e))
        if any(field in vals
               for field in ('active', 'group_id', 'user_id',
                             'network', 'private')):
            self._clear_caches()
        return super(IpAccessRule, self).write(vals)

    @api.multi
    def unlink(self):
        """ Clear caches when a rule removed """
        self._clear_caches()
        return super(IpAccessRule, self).unlink()

    @api.model_cr
    def _register_hook(self):
        """ Monkeypatch XML-RPC controller to allow access to remote address.
        See https://github.com/odoo/odoo/issues/24183. To remove in v12, and
        use normal odoo.http.request (courtesy of Jairo Llopis)

        Also do a runtime check on whether the ipaddress library is present.
        """
        original_fn = wsgi_server.application_unproxied

        def _patch(environ, start_response):
            current_thread().environ = environ
            return original_fn(environ, start_response)

        wsgi_server.application_unproxied = _patch

        if ipaddress is None:
            raise ValidationError(
                'Library ip2-ipaddress could not be loaded. Please install '
                'this library in the environment in which you run Odoo.')

        return super(IpAccessRule, self)._register_hook()
