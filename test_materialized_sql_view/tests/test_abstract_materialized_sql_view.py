# -*- coding: utf-8 -*-
# Copyright 2016 Pierre Verkest <pverkest@anybox.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .assertions import OpenErpAssertions
from openerp.exceptions import except_orm
from openerp.tests.common import TransactionCase


class AbstractMaterializedSqlViewTester(OpenErpAssertions, TransactionCase):

    def setUp(self):
        super(AbstractMaterializedSqlViewTester, self).setUp()
        self.demo_matview_mdl = self.env['test.materialized.view'].with_context(
            {'ascyn': False}
        )
        self.mat_view_mdl = self.env['materialized.sql.view']
        self.users_mdl = self.env['res.users']
        self.ref = self.env.ref
        self.user_id = self.ref('base.partner_demo')
        self.group_user = self.ref('base.group_user')

    def test_write_forbidden(self):
        rec = self.demo_matview_mdl.browse(self.group_user.id)
        self.assertRaises(except_orm, rec.write, {'name': "Test"})

    def test_unlink_forbidden(self):
        rec = self.demo_matview_mdl.browse(self.group_user.id)
        self.assertRaises(except_orm,
                          rec.unlink)

    def test_create_forbidden(self):
        self.assertRaises(except_orm, self.demo_matview_mdl.create,
                          {'name': 'Test'})

    def test_read_and_refresh_materialized_view(self):
        # Get the user_count for group_user.id
        group = self.demo_matview_mdl.browse(self.group_user.id)
        user_count = group.user_count
        # add user on group_user.id
        self.users_mdl.create({'name': u"Test user",
                               'login': u"ttt",
                               'company_id': self.ref('base.main_company').id,
                               'customer': False,
                               'email': 'demo@yourcompany.example.com',
                               'street': u"Avenue des Choux",
                               'city': u"Namue",
                               'zip': '5101',
                               'country_id': self.ref('base.be').id,
                               })
        # The user count havn't increase until we refresh the view
        self.assertEquals(
            self.demo_matview_mdl.browse(self.group_user.id).user_count,
            user_count
        )
        # Refresh the materialized view
        self.demo_matview_mdl.refresh_materialized_view()
        # Read user count (not in cache), there is one more now!
        self.assertEquals(
            group.read(['user_count'])[0]['user_count'],
            user_count + 1)

    def test_safe_properties(self):
        self.demo_matview_mdl._sql_mat_view_name = None
        self.demo_matview_mdl._sql_view_name = None
        self.assertEquals(
            self.demo_matview_mdl.sql_mat_view_name,
            self.demo_matview_mdl._table)
        self.assertEquals(self.demo_matview_mdl.sql_view_name,
                          self.demo_matview_mdl._table + '_view')
        sql = self.demo_matview_mdl.sql_view_definition
        self.demo_matview_mdl._sql_view_definition = None
        with self.assertRaises(ValueError):
            self.demo_matview_mdl.sql_view_definition
        # Set it back to iniatial value, this is used in some other unit test
        self.demo_matview_mdl._sql_view_definition = sql

    def test_change_matview_state(self):
        self.demo_matview_mdl.change_matview_state('after_refresh_view',
                                                   self.cr._cnx.server_version)
        self.assertRaises(AttributeError,
                          self.demo_matview_mdl.change_matview_state, 'test',
                          self.cr._cnx.server_version)

    def test_upgrade_db90300(self):
        if self.cr._cnx.server_version < 90300:
            # test upgrade impossible using pg server < 9.3
            return
        cr = self.env.cr
        ctxt = {'force_pg_version': 90200}
        matview_90200 = self.demo_matview_mdl.with_context(ctxt)
        ctxt = {'force_pg_version': 90300}
        matview_90300 = self.demo_matview_mdl.with_context(ctxt)
        # Drop existing view
        self.demo_matview_mdl.drop_materialized_view_if_exist(
            self.cr._cnx.server_version)
        # Force create view using pg 9.2 method
        matview_90200.create_materialized_view()
        # Make sure mat view relation is a table
        cr.execute("SELECT relkind FROM pg_class "
                   "WHERE relname = '%(relname)s'" %
                   {'relname': self.demo_matview_mdl.sql_mat_view_name})
        self.assertEquals(cr.fetchone()[0], 'r')
        # Run create again, using pg 9.3 method
        # We sould get a postgresql materialized view object 'm'
        matview_90300.create_or_upgrade_pg_matview_if_needs()
        cr.execute("SELECT relkind FROM pg_class "
                   "WHERE relname = '%(relname)s'" %
                   {'relname': self.demo_matview_mdl.sql_mat_view_name})
        self.assertEquals(cr.fetchone()[0], 'm')
        # Drop the view again and re-create view using pg 9.2 method
        # to test what's happen when running refresh without create
        self.demo_matview_mdl.drop_materialized_view_if_exist(90300)
        matview_90200.create_materialized_view()
        cr.execute("SELECT relkind FROM pg_class "
                   "WHERE relname = '%(relname)s'" %
                   {'relname': self.demo_matview_mdl.sql_mat_view_name})
        self.assertEquals(cr.fetchone()[0], 'r')
        matview_90300.refresh_materialized_view()
        cr.execute("SELECT relkind FROM pg_class "
                   "WHERE relname = '%(relname)s'" %
                   {'relname': self.demo_matview_mdl.sql_mat_view_name})
        self.assertEquals(cr.fetchone()[0], 'm')
        self.demo_matview_mdl.refresh_materialized_view()

    def test_upgrade_mat_view(self):
        self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs()
        self.assertEquals(
            [],
            self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs()
        )
        self.mat_view_mdl.write_values(
            self.demo_matview_mdl._sql_mat_view_name, {
                'sql_definition': 'SELECT 1'})
        self.assertNotEquals(
            [],
            self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs()
        )
        self.assertEquals(
            [],
            self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs())
        self.env.cr.execute("ALTER VIEW %s RENAME TO test" %
                            self.demo_matview_mdl._sql_view_name)
        self.mat_view_mdl.write_values(
            self.demo_matview_mdl._sql_mat_view_name, {'view_name': 'test'})
        self.assertNotEquals(
            [],
            self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs()
        )
        self.demo_matview_mdl.drop_materialized_view_if_exist(
            self.env.cr._cnx.server_version)
        self.assertNotEquals(
            [],
            self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs())

    def assert_calling_entry_points_method(
            self, method_name, calling_method, pg_version=None
    ):
        demo = self.demo_matview_mdl
        save_method = getattr(demo, method_name)
        self.called = False

        def mock_method():
            self.called = True

        setattr(demo, method_name, mock_method)
        if pg_version:
            getattr(demo, calling_method)(pg_version)
        else:
            getattr(demo, calling_method)()
        self.assertTrue(self.called)
        setattr(demo, method_name, save_method)
        demo.create_or_upgrade_pg_matview_if_needs()

    def test_overload_before_refresh(self):
        self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs()
        self.assert_calling_entry_points_method(
            'before_refresh_materialized_view', 'refresh_materialized_view'
        )

    def test_overload_after_refresh(self):
        self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs()
        self.assert_calling_entry_points_method(
            'after_refresh_materialized_view', 'refresh_materialized_view'
        )

    def test_overload_before_drop(self):
        self.assert_calling_entry_points_method(
            'before_drop_materialized_view', 'drop_materialized_view_if_exist',
            self.cr._cnx.server_version
        )

    def test_overload_after_drop(self):
        self.assert_calling_entry_points_method(
            'after_drop_materialized_view', 'drop_materialized_view_if_exist',
            self.cr._cnx.server_version
        )

    def test_overload_before_create(self):
        self.assert_calling_entry_points_method(
            'before_create_materialized_view', 'create_materialized_view'
        )

    def test_overload_after_create(self):
        self.assert_calling_entry_points_method(
            'after_create_materialized_view', 'create_materialized_view'
        )
