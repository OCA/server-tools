# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase
from datetime import datetime
from .assertions import OpenErpAssertions


class MaterializedSqlView(OpenErpAssertions, SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(MaterializedSqlView, cls).setUpClass()
        cls.matview_mdl = cls.registry('materialized.sql.view')
        cls.demo_matview_mdl = cls.registry('test.materialized.view')
        cls.users_mdl = cls.registry('res.users')

        cls.context = {'ascyn': False}
        mdl_id = cls.registry('ir.model').search(
            cls.cr, cls.uid, [
                ('model', '=', cls.demo_matview_mdl._name)])[0]
        values = {'name': u"Model test",
                  'model_id': mdl_id,
                  'sql_definition': cls.demo_matview_mdl.sql_view_definition,
                  'view_name': cls.demo_matview_mdl.sql_view_name,
                  'matview_name': cls.demo_matview_mdl.sql_mat_view_name,
                  'pg_version': 90205,
                  'state': 'nonexistent'
                  }
        cls.matview_id = cls.matview_mdl.create(
            cls.cr, cls.uid, values, context=cls.context)

    def test_simple_case(self):
        """Test some simple case, create/read/write/unlink"""
        users_mdl_id = self.registry('ir.model').search(
            self.cr, self.uid, [('model', '=', 'res.users')],
            context=self.context)[0]
        values = {'name': u"Test",
                  'model_id': users_mdl_id,
                  'sql_definition': 'SELECT 1',
                  'view_name': u'test_view',
                  'matview_name': 'test_mat_view_name',
                  'pg_version': 90305,
                  'last_refresh_start_date': datetime.now(),
                  'last_refresh_end_date': datetime.now(),
                  }
        id = self.matview_mdl.create(self.cr, self.uid, values)
        self.matview_mdl.write(self.cr, self.uid, [id], {'name': u"Fake test"},
                               context=self.context)
        values.update({'name': u"Fake test",
                       'state': u'nonexistent',
                       })
        # don't wan't to get headheak to fix format date here
        values.pop('last_refresh_start_date')
        values.pop('last_refresh_end_date')
        self.assertRecord(self.matview_mdl, id, values)
        self.matview_mdl.unlink(self.cr, self.uid, [id], context=self.context)

    def test_search_materialized_sql_view_ids_from_matview_name(self):
        mat_mdl = self.matview_mdl
        users_mdl_id = self.registry('ir.model').search(
            self.cr, self.uid, [('model', '=', 'res.users')],
            context=self.context)[0]
        values = {'name': u"Test",
                  'model_id': users_mdl_id,
                  'sql_definition': 'SELECT 1',
                  'view_name': u'test_view',
                  'matview_name': 'test_mat_view_name',
                  'pg_version': 90305,
                  'last_refresh_start_date': datetime.now(),
                  'last_refresh_end_date': datetime.now(),
                  }
        id = self.matview_mdl.create(self.cr, self.uid, values)
        self.assertEquals(
            [id],
            mat_mdl.search_materialized_sql_view_ids_from_matview_name(
                self.cr,
                self.uid,
                'test_mat_view_name',
                context=self.context))

    def test_launch_refresh_materialized_sql_view(self):
        cr, uid, mat_mdl = self.cr, self.uid, self.matview_mdl
        group_id = self.ref('base.group_user')
        user_count = self.demo_matview_mdl.read(
            cr, uid, group_id, ['user_count'])['user_count']
        self.users_mdl.create(cr,
                              uid,
                              {'name': u"Test user",
                               'login': u"ttt",
                               'company_id': self.ref('base.main_company'),
                                  'customer': False,
                                  'email': 'demo@yourcompany.example.com',
                                  'street': u"Avenue des Choux",
                                  'city': u"Namue",
                                  'zip': '5101',
                                  'country_id': self.ref('base.be'),
                               },
                              context=self.context)
        self.assertEquals(
            self.demo_matview_mdl.read(cr, uid, group_id, ['user_count'],
                                       context=self.context)['user_count'],
            user_count)
        ids = mat_mdl.search_materialized_sql_view_ids_from_matview_name(
            cr, uid, self.demo_matview_mdl._sql_mat_view_name)
        self.matview_mdl.launch_refresh_materialized_sql_view(
            cr, uid, ids, context=self.context)
        self.assertEquals(
            self.demo_matview_mdl.read(cr, uid, group_id, ['user_count'],
                                       context=self.context)['user_count'],
            user_count + 1)
        for rec in mat_mdl.read(cr, uid, ids, ['state'], context=self.context):
            self.assertEquals(rec['state'], 'refreshed')

    def test_launch_refresh_materialized_sql_view_by_name(self):
        cr, uid, mat_mdl = self.cr, self.uid, self.matview_mdl
        group_id = self.ref('base.group_user')

        user_count = self.demo_matview_mdl.read(
            cr, uid, group_id, ['user_count'])['user_count']
        self.users_mdl.create(cr,
                              uid,
                              {'name': u"Test user2",
                               'login': u"test2",
                               'company_id': self.ref('base.main_company'),
                                  'customer': False,
                                  'email': 'demo@yourcompany.example.com',
                                  'street': u"Avenue des Choux",
                                  'city': u"Namue",
                                  'zip': '5101',
                                  'country_id': self.ref('base.be'),
                               },
                              context=self.context)
        self.assertEquals(
            self.demo_matview_mdl.read(cr, uid, group_id, ['user_count'],
                                       context=self.context)['user_count'],
            user_count)
        ids = mat_mdl.search_materialized_sql_view_ids_from_matview_name(
            cr, uid, self.demo_matview_mdl._sql_mat_view_name)
        self.matview_mdl.refresh_materialized_view_by_name(
            cr, uid, self.demo_matview_mdl._sql_mat_view_name,
            context=self.context)
        for rec in mat_mdl.read(cr, uid, ids, ['state'], context=self.context):
            self.assertEquals(rec['state'], 'refreshed')
        # Read user count, there is one more now!
        self.assertEquals(
            self.demo_matview_mdl.read(cr, uid, group_id, ['user_count'],
                                       context=self.context)['user_count'],
            user_count + 1)

    def test_before_create_view(self):
        self.matview_mdl.before_create_view(
            self.cr, self.uid, self.demo_matview_mdl._sql_mat_view_name,
            context=self.context)
        self.assertRecord(self.matview_mdl, self.matview_id,
                          {'state': 'creating',
                           'last_error_message': '',
                           })

    def test_before_refresh_view(self):
        self.matview_mdl.before_refresh_view(
            self.cr, self.uid, self.demo_matview_mdl._sql_mat_view_name,
            context=self.context)
        self.assertRecord(self.matview_mdl, self.matview_id,
                          {'state': 'refreshing',
                           'last_error_message': '',
                           })

    def test_after_refresh_view(self):
        self.matview_mdl.after_refresh_view(
            self.cr, self.uid, self.demo_matview_mdl._sql_mat_view_name,
            context=self.context)
        self.assertRecord(self.matview_mdl, self.matview_id,
                          {'state': 'refreshed',
                           'last_error_message': '',
                           })

    def test_after_drop_view(self):
        self.matview_mdl.after_drop_view(
            self.cr, self.uid, self.demo_matview_mdl._sql_mat_view_name,
            context=self.context)
        self.assertRecord(self.matview_mdl, self.matview_id,
                          {'state': 'nonexistent',
                           'last_error_message': '',
                           })

    def test_aborted_matview(self):
        self.context.update({'error_message': u"Error details"})
        self.matview_mdl.aborted_matview(
            self.cr, self.uid, self.demo_matview_mdl._sql_mat_view_name,
            context=self.context)
        self.assertRecord(self.matview_mdl, self.matview_id,
                          {'state': 'aborted',
                           'last_error_message': u"Error details",
                           })

    def test_create_if_not_exist(self):
        cr, uid = self.cr, self.uid
        count = self.matview_mdl.search(
            cr, uid, [('view_name', '=', 'test_123')], count=True)
        self.matview_mdl.create_if_not_exist(
            cr, uid, {'model_name': self.demo_matview_mdl._name,
                      'sql_definition': 'SELECT 1',
                      'view_name': 'test_123',
                      'matview_name': 'test_123_view',
                      'pg_version': cr._cnx.server_version,
                      }, context=self.context)
        self.assertEquals(
            count + 1,
            self.matview_mdl.search(
                cr, uid, [('view_name', '=', 'test_123')], count=True)
        )
        self.matview_mdl.create_if_not_exist(
            cr, uid, {'model_name': self.demo_matview_mdl._name,
                      'sql_definition': 'SELECT 1',
                      'view_name': 'test_123',
                      'matview_name': 'test_123_view',
                      'pg_version': cr._cnx.server_version,
                      }, context=self.context)
        self.assertEquals(
            count + 1,
            self.matview_mdl.search(
                cr, uid, [('view_name', '=', 'test_123')], count=True)
        )
        self.matview_mdl.create_if_not_exist(
            cr, uid, {'model_name': self.demo_matview_mdl._name,
                      'sql_definition': 'SELECT 1',
                      'view_name': 'test_123',
                      'matview_name': 'test_123_view',
                      'pg_version': 90402,
                      }, context=self.context)
        self.assertEquals(
            count + 1,
            self.matview_mdl.search(
                cr, uid, [('view_name', '=', 'test_123')], count=True)
        )
