# -*- coding: utf-8 -*-
# Copyright 2016-2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=missing-docstring
from contextlib import contextmanager
from odoo.tests.common import TransactionCase


class PatchLDAPConnection(object):
    # pylint: disable=no-self-use,unused-argument,too-many-arguments
    def __init__(self, results):
        self.results = results

    def simple_bind_s(self, user, password):
        return True

    def search_st(self, base, scope, ldap_filter, attributes, timeout=None):
        if ldap_filter == '(uid=*)':
            return self.results
        raise Exception("Invalid filter %s" % ldap_filter)

    def unbind(self):
        return True


@contextmanager
def patch_ldap(results):
    """ defuse ldap functions to return fake entries instead of talking to a
    server. Use this in your own ldap related tests """
    import ldap
    original_initialize = ldap.initialize

    def initialize(uri):  # pylint: disable=unused-argument
        return PatchLDAPConnection(results)
    ldap.initialize = initialize
    yield
    ldap.initialize = original_initialize


def get_fake_ldap(self):
    company = self.env.ref('base.main_company')
    company.write({
        'ldaps': [(0, 0, {
            'ldap_server': 'fake',
            'ldap_server_port': 389,
            'ldap_filter': '(uid=%s)',
            'ldap_base': 'fake',
            'deactivate_unknown_users': True,
            'no_deactivate_user_ids': [(6, 0, [
                self.env.ref('base.user_root').id,
            ])],
        })],
    })
    return company.ldaps.filtered(
        lambda x: x.ldap_server == 'fake'
    )


EXPECTED_RESULTS = [
    ('DN=fake', {
        'cn': ['fake'],
        'uid': ['fake'],
        'mail': ['fake@fakery.com']})]


class TestUsersLdapPopulate(TransactionCase):

    def test_populate(self):
        with patch_ldap(EXPECTED_RESULTS):
            get_fake_ldap(self).populate_wizard()
            self.assertFalse(self.env.ref('base.user_demo').active)
            self.assertTrue(self.env.ref('base.user_root').active)
            self.assertTrue(self.env['res.users'].search([
                ('login', '=', 'fake')
            ]))

    def test_populate_exception(self):
        with patch_ldap(EXPECTED_RESULTS):
            fake_ldap = get_fake_ldap(self)
            fake_ldap.ldap_filter = '(not_a_uid=%s)'
            with self.assertRaises(Exception):
                fake_ldap.populate_wizard()
