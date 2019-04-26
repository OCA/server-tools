# -*- coding: utf-8 -*-
# Copyright 2012-2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=missing-docstring,invalid-name,protected-access
import logging
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)

try:
    import ldap
    from ldap.filter import filter_format
except ImportError:
    _logger.debug('Cannot import ldap.')


class ResCompanyLDAP(models.Model):
    _inherit = 'res.company.ldap'

    deactivate_unknown_users = fields.Boolean(
        string='Deactivate unknown users',
        default=False,
    )

    @api.multi
    def action_populate(self):
        """Prepopulate the user table from one or more LDAP resources.

        Obviously, the option to create users must be toggled in
        the LDAP configuration.

        Return the number of users created (as far as we can tell).
        """
        deactivated_users_count = 0
        users_model = self.env['res.users']
        synchronization_time = fields.Datetime.now()
        for this in self:
            if (not this.ldap_server) or (not this.create_user):
                continue
            _logger.debug(
                "action_populate called on ldap server %s", this.ldap_server)
            login_attr = this._get_login_attribute()
            conf = this.read([])[0]
            ldap_entries = this.get_ldap_entries(conf)
            for ldap_entry in ldap_entries:
                login = ldap_entry[1][login_attr][0].lower().strip()
                # Read al fields to get configuration as dictionary
                user_id = self.with_context(
                    no_reset_password=True
                ).get_or_create_user(conf, login, ldap_entry)
                ldap_user = \
                    users_model.browse(user_id) if user_id else \
                    this._reactivate_user(login)
                ldap_user.write({
                    'ldap_id': this.id,
                    'last_synchronization': synchronization_time})
            if this.deactivate_unknown_users:
                deactivated_users_count += \
                    this._deactivate_unknown_users(synchronization_time)
        users_created = users_model.search_count(
            [('create_date', '>=', synchronization_time)])
        _logger.debug("%d users created", users_created)
        _logger.debug("%d users deactivated", deactivated_users_count)
        return users_created, deactivated_users_count

    @api.multi
    def _get_login_attribute(self):
        """Get the ldap attribute that will contain the user login name."""
        self.ensure_one()
        attribute_match = re.search(r'([a-zA-Z_]+)=\%s', self.ldap_filter)
        if not attribute_match:
            raise UserError(
                _("No login attribute found: "
                  "Could not extract login attribute from filter %s") %
                self.ldap_filter)
        return attribute_match.group(1)

    @api.multi
    def get_ldap_entries(self, conf, user_name='*', timeout=60):
        """Execute ldap query as defined in conf.

        Don't call self.query because it supresses possible exceptions
        """
        self.ensure_one()
        ldap_filter = filter_format(self.ldap_filter % user_name, ())
        conn = self.connect(conf)
        conn.simple_bind_s(
            self.ldap_binddn or '',
            self.ldap_password or '')
        try:
            results = conn.search_st(
                self.ldap_base, ldap.SCOPE_SUBTREE,
                ldap_filter.encode('utf8'), None, timeout=timeout)
        except Exception:
            _logger.error(_(
                'Error searching with filter %s'), ldap_filter, exc_info=True)
            raise
        conn.unbind()
        return results

    @api.model
    def _reactivate_user(self, login):
        """Reactivate user that is in ldap, but neither found nor created."""
        users_model = self.env['res.users']
        # this happens if the user exists but is active = False
        # -> fetch the user again and reactivate it
        self.env.cr.execute(
            "SELECT id FROM res_users "
            "WHERE lower(login)=%s",
            (login,))
        res = self.env.cr.fetchone()
        if not res:
            raise UserError(_(
                'Unable to process user with login %s') % login)
        _logger.debug('unarchiving user %s', login)
        user = users_model.browse(res[0])
        user.write({'active': True})
        return user

    @api.multi
    def _deactivate_unknown_users(self, synchronization_time):
        """Deactivate users not found in last populate run."""
        self.ensure_one()
        users_model = self.env['res.users']
        _logger.debug(_("Deactivate unknown users for %s"), self.ldap_server)
        unknown_users = users_model.search([
            ('ldap_id', '=', self.id),
            ('active', '=', True),
            ('last_synchronization', '<', synchronization_time)])
        for unknown_user in unknown_users:
            _logger.debug(_("archiving user %s"), unknown_user.login)
        unknown_users.write({'active': False})
        return len(unknown_users)

    @api.multi
    def populate_wizard(self):
        """
        GUI wrapper for the populate method that reports back
        the number of users created.
        """
        self.ensure_one()
        wizard_obj = self.env['res.company.ldap.populate_wizard']
        res_id = wizard_obj.create({'ldap_id': self.id}).id
        return {
            'name': wizard_obj._description,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': wizard_obj._name,
            'domain': [],
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': res_id,
            'nodestroy': True,
        }
