# -*- coding: utf-8 -*-
# © 2012 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

import re

from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

try:
    from ldap.filter import filter_format
except ImportError:
    _logger.debug('Can not `from ldap.filter import filter_format`.')


class CompanyLDAP(models.Model):
    _inherit = 'res.company.ldap'

    @api.multi
    def action_populate(self):
        """
        Prepopulate the user table from one or more LDAP resources.

        Obviously, the option to create users must be toggled in
        the LDAP configuration.

        Return the number of users created (as far as we can tell).
        """
        users_pool = self.env['res.users']
        users_no_before = users_pool.search_count([])
        logger = logging.getLogger('orm.ldap')
        logger.debug("action_populate called on res.company.ldap ids %s",
                     self.ids)

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
            ldap_filter = filter_format(conf['ldap_filter'] % '*', ())
            for result in self.query(conf, ldap_filter.encode('utf-8')):
                self.get_or_create_user(conf, result[1][login_attr][0], result)

        users_no_after = users_pool.search_count([])
        users_created = users_no_after - users_no_before
        logger.debug("%d users created", users_created)
        return users_created

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
