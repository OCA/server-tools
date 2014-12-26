# -*- coding: utf-8 -*-
from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.osv import osv
from openerp import SUPERUSER_ID


class AbstractMaterializedSqlViewTester(SharedSetupTransactionCase):

    @classmethod
    def initTestData(self):
        super(AbstractMaterializedSqlViewTester, self).initTestData()
        self.demo_matview_mdl = self.registry('test.materialized.view')
        self.mat_view_mdl = self.registry('materialized.sql.view')
        self.users_mdl = self.registry('res.users')
        self.context = {'ascyn': False}
        self.ref = self.env.ref
        self.user_id = self.ref('base.partner_demo').id
        self.group_id = self.ref('base.group_user').id

    def test_write_forbidden(self):
        self.assertRaises(osv.except_osv,
                          self.demo_matview_mdl.write,
                          self.cr, self.uid, [self.group_id], {'name': 'Test'})

    def test_unlink_forbidden(self):
        self.assertRaises(osv.except_osv,
                          self.demo_matview_mdl.unlink,
                          self.cr, self.uid, [self.group_id],
                          context=self.context)

    def test_create_forbidden(self):
        self.assertRaises(osv.except_osv,
                          self.demo_matview_mdl.unlink,
                          self.cr, self.uid, {'name': 'Test'},
                          context=self.context)

    def test_read_and_refresh_materialized_view(self):
        cr, uid = self.cr, self.uid
        # Get the user_count for group_id
        user_count = self.demo_matview_mdl.read(
            cr, uid, self.group_id, ['user_count'],
            context=self.context)['user_count']
        # add user on group_id
        self.users_mdl.create(cr,
                              uid,
                              {'name': u"Test user",
                               'login': u"ttt",
                               'company_id': self.ref('base.main_company').id,
                                  'customer': False,
                                  'email': 'demo@yourcompany.example.com',
                                  'street': u"Avenue des Choux",
                                  'city': u"Namue",
                                  'zip': '5101',
                                  'country_id': self.ref('base.be').id,
                               },
                              context=self.context)
        # The user count havn't increase until we refresh the view
        self.assertEquals(self.demo_matview_mdl.read(
            cr, uid, self.group_id, ['user_count'],
            context=self.context)['user_count'],
            user_count)
        # Refresh the materialized view
        self.demo_matview_mdl.refresh_materialized_view(
            cr, SUPERUSER_ID, context=self.context)
        # Read user count, there is one more now!
        self.assertEquals(self.demo_matview_mdl.read(
            cr, uid, self.group_id, ['user_count'],
            context=self.context)['user_count'],
            user_count + 1)

    def test_safe_properties(self):
        self.demo_matview_mdl._sql_mat_view_name = ''
        self.demo_matview_mdl._sql_view_name = ''
        self.demo_matview_mdl.safe_properties()
        self.assertEquals(
            self.demo_matview_mdl._sql_mat_view_name,
            self.demo_matview_mdl._table)
        self.assertEquals(self.demo_matview_mdl._sql_view_name,
                          self.demo_matview_mdl._table + '_view')
        sql = self.demo_matview_mdl._sql_view_definition
        self.demo_matview_mdl._sql_view_definition = ''
        self.assertRaises(osv.except_osv,
                          self.demo_matview_mdl.safe_properties
                          )
        # Set it back to iniatial value, this is used in some other unit test
        self.demo_matview_mdl._sql_view_definition = sql

    def test_change_matview_state(self):
        self.demo_matview_mdl.change_matview_state(self.cr, self.uid,
                                                   'after_refresh_view',
                                                   self.cr._cnx.server_version,
                                                   context=self.context)
        self.assertRaises(AttributeError,
                          self.demo_matview_mdl.change_matview_state, self.cr,
                          self.uid, 'test',
                          self.cr._cnx.server_version)

    def test_upgrade_db90300(self):
        if self.cr._cnx.server_version < 90300:
            # test upgrade impossible using pg server < 9.3
            return
        ctxt, cr = self.context, self.cr
        # Drop existing view
        self.demo_matview_mdl.drop_materialized_view_if_exist(
            cr, SUPERUSER_ID, self.cr._cnx.server_version, context=ctxt)
        # Force create view using pg 9.2 method
        ctxt.update({'force_pg_version': 90200})
        self.demo_matview_mdl.create_materialized_view(
            cr, SUPERUSER_ID, context=ctxt)
        # Make sure mat view relation is a table
        cr.execute("SELECT relkind FROM pg_class "
                   "WHERE relname = '%(relname)s'" %
                   {'relname': self.demo_matview_mdl._sql_mat_view_name})
        self.assertEquals(cr.fetchone()[0], 'r')
        # Run create again, using pg 9.3 method
        # We sould get materialized view
        ctxt.update({'force_pg_version': 90300})
        self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs(
            cr, SUPERUSER_ID, context=ctxt)
        cr.execute("SELECT relkind FROM pg_class "
                   "WHERE relname = '%(relname)s'" %
                   {'relname': self.demo_matview_mdl._sql_mat_view_name})
        self.assertEquals(cr.fetchone()[0], 'm')
        # Drop the view again and re-create view using pg 9.2 method
        # to test what's happen when running refresh without create
        self.demo_matview_mdl.drop_materialized_view_if_exist(
            cr, SUPERUSER_ID, 90300, context=ctxt)
        ctxt.update({'force_pg_version': 90200})
        self.demo_matview_mdl.create_materialized_view(
            cr, SUPERUSER_ID, context=ctxt)
        cr.execute("SELECT relkind FROM pg_class "
                   "WHERE relname = '%(relname)s'" %
                   {'relname': self.demo_matview_mdl._sql_mat_view_name})
        self.assertEquals(cr.fetchone()[0], 'r')
        ctxt.update({'force_pg_version': 90300})
        self.demo_matview_mdl.refresh_materialized_view(
            cr, SUPERUSER_ID, context=ctxt)
        cr.execute("SELECT relkind FROM pg_class "
                   "WHERE relname = '%(relname)s'" %
                   {'relname': self.demo_matview_mdl._sql_mat_view_name})
        self.assertEquals(cr.fetchone()[0], 'm')
        ctxt.pop('force_pg_version')
        self.demo_matview_mdl.refresh_materialized_view(
            cr, SUPERUSER_ID, context=ctxt)

    def test_upgrade_mat_view(self):
        ctxt, cr, uid = self.context, self.cr, self.uid
        self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs(
            cr, SUPERUSER_ID, context=ctxt)
        self.assertEquals(
            [],
            self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs(
                cr, SUPERUSER_ID, context=ctxt)
        )
        self.mat_view_mdl.write_values(
            cr, uid, self.demo_matview_mdl._sql_mat_view_name, {
                'sql_definition': 'SELECT 1'}, context=ctxt)
        self.assertNotEquals(
            [],
            self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs(
                cr, SUPERUSER_ID, context=ctxt)
        )
        self.assertEquals(
            [],
            self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs(
                cr, SUPERUSER_ID, context=ctxt))
        cr.execute("ALTER VIEW %s RENAME TO test" %
                   self.demo_matview_mdl._sql_view_name)
        self.mat_view_mdl.write_values(
            cr, uid, self.demo_matview_mdl._sql_mat_view_name, {
                'view_name': 'test'}, context=ctxt)
        self.assertNotEquals(
            [],
            self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs(
                cr, SUPERUSER_ID, context=ctxt)
        )
        self.demo_matview_mdl.drop_materialized_view_if_exist(
            cr, uid, cr._cnx.server_version, context=ctxt)
        self.assertNotEquals(
            [],
            self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs(
                cr, SUPERUSER_ID, context=ctxt))
