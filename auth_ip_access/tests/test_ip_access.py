# coding: utf-8
# Copyright 2020 Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from threading import current_thread
from odoo.exceptions import AccessDenied
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


def patch_cursor(func):
    """ Decorator that patches the current TestCursor for nested savepoint
    support """
    def acquire(cursor):
        cursor._depth += 1
        cursor._lock.acquire()
        cursor.execute("SAVEPOINT test_cursor%d" % cursor._depth)

    def release(cursor):
        cursor.execute("RELEASE SAVEPOINT test_cursor%d" % cursor._depth)
        cursor._depth -= 1
        cursor._lock.release()

    def close(cursor):
        cursor.release()

    def commit(cursor):
        cursor.execute("RELEASE SAVEPOINT test_cursor%d" % cursor._depth)
        cursor.execute("SAVEPOINT test_cursor%d" % cursor._depth)

    def rollback(cursor):
        cursor.execute(
            "ROLLBACK TO SAVEPOINT test_cursor%d" % cursor._depth)
        cursor.execute("SAVEPOINT test_cursor%d" % cursor._depth)

    def wrapped_function(self, *args):
        with self.cursor() as cursor:
            cursor.execute("SAVEPOINT test_cursor0")
            cursor._depth = 1
            cursor.execute("SAVEPOINT test_cursor%d" % cursor._depth)

            cursor.__acquire = cursor.acquire
            cursor.__release = cursor.release
            cursor.__commit = cursor.commit
            cursor.__rollback = cursor.rollback
            cursor.__close = cursor.close
            cursor.acquire = lambda: acquire(cursor)
            cursor.release = lambda: release(cursor)
            cursor.commit = lambda: commit(cursor)
            cursor.rollback = lambda: rollback(cursor)
            cursor.close = lambda: close(cursor)

        try:
            func(self, *args)
        finally:
            with self.cursor() as cursor:
                cursor.acquire = cursor.__acquire
                cursor.release = cursor.__release
                cursor.commit = cursor.__commit
                cursor.rollback = cursor.__rollback
                cursor.close = cursor.__close

    return wrapped_function


class TestIpAccess(TransactionCase):

    def setUp(self):
        super(TestIpAccess, self).setUp()
        self.registry.enter_test_mode()
        self.env = self.env(cr=self.cursor())

    def tearDown(self):
        self.registry.leave_test_mode()
        super(TestIpAccess, self).tearDown()

    @patch_cursor
    @mute_logger('odoo.addons.auth_ip_access.models.res_users')
    def test_ip_access(self):
        self.env['ip.access.rule'].search([]).unlink()
        password = 'test'
        self.env.user.password = password

        # Emulate the patching of the environ on the thread
        environ = {'REMOTE_ADDR': '192.168.1.50'}
        current_thread().environ = environ

        # No rules, all access granted
        self.env.user.check_credentials(password)

        # Matching rule amongst a number of rules for the user's groups
        # grants access too
        rule_nomatch = self.env['ip.access.rule'].create({
            'group_id': self.env.user.groups_id[0].id,
            'network': '10.0.0.1',
        })
        rule = self.env['ip.access.rule'].create({
            'group_id': self.env.user.groups_id[0].id,
            'network': '192.168.1.50',
        })
        self.env.user.check_credentials(password)

        # Matching rule does not apply without a group match
        rule.group_id = self.env['res.groups'].search(
            [('id', 'not in', self.env.user.groups_id.ids)], limit=1)
        with self.assertRaises(AccessDenied):
            self.env.user.check_credentials(password)

        # Rule becomes universal without a group
        rule.group_id = False
        self.env.user.check_credentials(password)
        # Or can be specific for a single user
        rule.user_id = self.env.ref('base.user_demo')
        with self.assertRaises(AccessDenied):
            self.env.user.check_credentials(password)
        rule.user_id = self.env.user
        self.env.user.check_credentials(password)

        # Only applicable rule does not grant access
        rule.network = '192.168.1.51'
        with self.assertRaises(AccessDenied):
            self.env.user.check_credentials(password)

        # All rules for the user's groups are inactive, granting access
        rule_nomatch.active = False
        rule.active = False
        self.env.user.check_credentials(password)
        rule.active = True
        with self.assertRaises(AccessDenied):
            self.env.user.check_credentials(password)

        # Add new rule that does grant access by netmask
        rule2 = self.env['ip.access.rule'].create({
            'group_id': self.env.user.groups_id[0].id,
            'network': '192.168.1.0/24',
        })
        self.env.user.check_credentials(password)

        # Access by private address
        rule2.write({'network': False, 'private': True})
        self.env.user.check_credentials(password)

        # The private address rule does not grant access to a global address
        environ['REMOTE_ADDR'] = '8.8.8.8'
        with self.assertRaises(AccessDenied):
            self.env.user.check_credentials(password)
