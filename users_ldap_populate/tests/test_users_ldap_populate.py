# -*- coding: utf-8 -*-
# Copyright 2016-2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=missing-docstring
from contextlib import contextmanager

from odoo.tools import mute_logger
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


EXPECTED_RESULTS = [
    ('DN=fake', {
        'cn': ['fake'],
        'uid': ['fake'],
        'mail': ['fake@example.com']})]


class TestUsersLdapPopulate(TransactionCase):

    # Without post_install and at_install tests will fail on existing
    # databases due to required (and therefore not NULL) fields added to
    # res.partner, for instance in account module. Of course inheriting
    # models should Never set fields to required, but it happens in many
    # existing modules anyway.
    post_install = True
    at_install = False

    def setUp(self):  # pylint: disable=invalid-name
        super(TestUsersLdapPopulate, self).setUp()
        self.user_model = self.env['res.users']
        self.ldap_model = self.env['res.company.ldap']
        self.fake_ldap = self.ldap_model.create({
            'company': self.env.ref('base.main_company').id,
            'ldap_server': 'fake',
            'ldap_server_port': 389,
            'ldap_filter': '(uid=%s)',
            'ldap_base': 'fake',
            'deactivate_unknown_users': True})

    def test_populate(self):
        with patch_ldap(EXPECTED_RESULTS):
            self.env.ref('base.user_demo').write({
                'ldap_id': self.fake_ldap.id,
                'last_synchronization': '2000-02-28'})  # long ago...
            self.fake_ldap.populate_wizard()
            self.assertFalse(self.env.ref('base.user_demo').active)
            self.assertTrue(self.env.ref('base.user_root').active)
            self.assertTrue(self.user_model.search([('login', '=', 'fake')]))

    def test_reactivate(self):
        with patch_ldap(EXPECTED_RESULTS):
            self.fake_ldap.populate_wizard()
            # we should have the fake user now.
            fake_user = self.user_model.search(
                [('login', '=', 'fake')], limit=1)
            self.assertTrue(fake_user)
            fake_user.write({'active': False})
            self.fake_ldap.populate_wizard()
            self.assertTrue(fake_user.active)

    @mute_logger("odoo.addons.users_ldap_populate.models.res_company_ldap")
    def test_populate_exception(self):
        with patch_ldap(EXPECTED_RESULTS):
            self.fake_ldap.ldap_filter = '(not_a_uid=%s)'
            with self.assertRaises(Exception):
                self.fake_ldap.populate_wizard()
