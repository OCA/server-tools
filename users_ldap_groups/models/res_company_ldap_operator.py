# -*- coding: utf-8 -*-
# © 2012-2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from logging import getLogger
from odoo import api, models
from string import Template
_logger = getLogger(__name__)


class ResCompanyLdapOperator(models.AbstractModel):
    """Define operators for group mappings"""

    _name = "res.company.ldap.operator"
    _description = "Definition op LDAP operations"

    @api.model
    def operators(self):
        """Return names of function to call on this model as operator"""
        return ('contains', 'equals', 'query')

    @api.model
    def contains(self, ldap_entry, mapping):
        return mapping.ldap_attribute in ldap_entry[1] and \
            mapping.value in ldap_entry[1][mapping.ldap_attribute]

    def equals(self, ldap_entry, mapping):
        return mapping.ldap_attribute in ldap_entry[1] and \
            unicode(mapping.value) == unicode(
                ldap_entry[1][mapping.ldap_attribute]
            )

    def query(self, ldap_entry, mapping):
        query_string = Template(mapping.value).safe_substitute({
            attr: ldap_entry[1][attr][0] for attr in ldap_entry[1]
        })
        _logger.debug(
            'evaluating query group mapping, filter: %s' % query_string
        )
        results = mapping.ldap_id.query(
            mapping.ldap_id.read()[0], query_string
        )
        _logger.debug(results)
        return bool(results)
