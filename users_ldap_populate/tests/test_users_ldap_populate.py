# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase
from contextlib import contextmanager


class patch_ldap_connection(object):
    def __init__(self, results):
        self.results = results

    def simple_bind_s(self, user, password):
        return True

    def search_st(self, base, scope, ldap_filter, attributes, timeout=None):
        if ldap_filter == '(uid=*)':
            return self.results
        else:
            return []

    def unbind(self):
        return True


@contextmanager
def patch_ldap(self, results):
    """ defuse ldap functions to return fake entries instead of talking to a
    server. Use this in your own ldap related tests """
    import ldap
    original_initialize = ldap.initialize

    def initialize(uri):
        return patch_ldap_connection(results)
    ldap.initialize = initialize
    yield
    ldap.initialize = original_initialize


def get_fake_ldap(self):
    company = self.env.ref('base.main_company')
    company.write({
        'ldaps': [(0, 0, {
            'ldap_server': 'fake',
            'ldap_port': 'fake',
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


class TestUsersLdapPopulate(TransactionCase):
    def test_users_ldap_populate(self):
        with patch_ldap(self, [('DN=fake', {
            'cn': ['fake'],
            'uid': ['fake'],
            'mail': ['fake@fakery.com'],
        })]):
            get_fake_ldap(self).populate_wizard()
            self.assertFalse(self.env.ref('base.user_demo').active)
            self.assertTrue(self.env.ref('base.user_root').active)
            self.assertTrue(self.env['res.users'].search([
                ('login', '=', 'fake')
            ]))
