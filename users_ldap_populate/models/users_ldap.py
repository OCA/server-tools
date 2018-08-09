# -*- coding: utf-8 -*-
# © 2012 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

import re

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

try:
    import ldap
    from ldap.filter import filter_format
except ImportError:
    _logger.debug('Cannot import ldap.')


class CompanyLDAP(models.Model):
    _inherit = 'res.company.ldap'

    no_deactivate_user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='res_company_ldap_no_deactivate_user_rel',
        column1='ldap_id',
        column2='user_id',
        string='Users never to deactivate',
        help='List users who never should be deactivated by'
             ' the deactivation wizard',
        default=lambda self: [(6, 0, [SUPERUSER_ID])],
    )
    deactivate_unknown_users = fields.Boolean(
        string='Deactivate unknown users',
        default=False,
    )

    @api.multi
    def action_populate(self):
        """
        Prepopulate the user table from one or more LDAP resources.

        Obviously, the option to create users must be toggled in
        the LDAP configuration.

        Return the number of users created (as far as we can tell).
        """
        logger = logging.getLogger('orm.ldap')
        logger.debug(
            "action_populate called on res.company.ldap ids %s", self.ids)

        users_model = self.env['res.users']
        users_count_before = users_model.search_count([])

        deactivate_unknown, known_user_ids = self._check_users()
        if deactivate_unknown:
            logger.debug("will deactivate unknown users")
        for conf in self.get_ldap_dicts():
            if not conf['create_user']:
                continue
            attribute_match = re.search(
                r'([a-zA-Z_]+)=\%s', conf['ldap_filter'])
            if attribute_match:
                login_attr = attribute_match.group(1)
            else:
                raise UserError(
                    _("No login attribute found: "
                      "Could not extract login attribute from filter %s") %
                    conf['ldap_filter'])
            results = self.get_ldap_entry_dicts(conf)
            for result in results:
                user_id = self.with_context(
                    no_reset_password=True
                ).get_or_create_user(conf, result[1][login_attr][0], result)
                # this happens if something goes wrong while creating the user
                # or fetching information from ldap
                if not user_id:
                    deactivate_unknown = False
                known_user_ids.append(user_id)

        users_created = users_model.search_count([]) - users_count_before

        deactivated_users_count = 0
        if deactivate_unknown:
            deactivated_users_count = \
                self.do_deactivate_unknown_users(known_user_ids)

        logger.debug("%d users created", users_created)
        logger.debug("%d users deactivated", deactivated_users_count)
        return users_created, deactivated_users_count

    def _check_users(self):
        deactivate_unknown = None
        known_user_ids = [self.env.user.id]
        for item in self.read(['no_deactivate_user_ids',
                               'deactivate_unknown_users'],
                              load='_classic_write'):
            if deactivate_unknown is None:
                deactivate_unknown = True
            known_user_ids.extend(item['no_deactivate_user_ids'])
            deactivate_unknown &= item['deactivate_unknown_users']
        return deactivate_unknown, known_user_ids

    def get_ldap_entry_dicts(self, conf, user_name='*'):
        """Execute ldap query as defined in conf.

        Don't call self.query because it supresses possible exceptions
        """
        ldap_filter = filter_format(conf['ldap_filter'] % user_name, ())
        conn = self.connect(conf)
        conn.simple_bind_s(conf['ldap_binddn'] or '',
                           conf['ldap_password'] or '')
        results = conn.search_st(conf['ldap_base'], ldap.SCOPE_SUBTREE,
                                 ldap_filter.encode('utf8'), None,
                                 timeout=60)
        conn.unbind()
        return results

    def do_deactivate_unknown_users(self, known_user_ids):
        """Deactivate users not found in last populate run."""
        unknown_user_ids = []
        users = self.env['res.users'].search(
            [('id', 'not in', known_user_ids)])
        for unknown_user in users:
            present_in_ldap = False
            for conf in self.get_ldap_dicts():
                present_in_ldap |= bool(self.get_ldap_entry_dicts(
                    conf, user_name=unknown_user.login))
            if not present_in_ldap:
                unknown_user.active = False
                unknown_user_ids.append(unknown_user.id)
        return len(unknown_user_ids)

    @api.multi
    def populate_wizard(self):
        """
        GUI wrapper for the populate method that reports back
        the number of users created.
        """
        if not self:
            return
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
