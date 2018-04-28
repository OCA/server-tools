# -*- coding: utf-8 -*-
# Copyright 2016 Pierre Verkest <pverkest@anybox.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SingleTransactionCase
from datetime import datetime
from .assertions import OpenErpAssertions


class MaterializedSqlView(OpenErpAssertions, SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(MaterializedSqlView, cls).setUpClass()
        cls.matview_mdl = cls.env['materialized.sql.view']
        cls.demo_matview_mdl = cls.env['test.materialized.view'].with_context(
            {'ascyn': False})
        cls.users_mdl = cls.env['res.users']
        mdl_id = cls.env['ir.model'].search(
            [('model', '=', cls.demo_matview_mdl._name)]).ids[0]
        values = {'name': u"Model test",
                  'model_id': mdl_id,
                  'sql_definition': cls.demo_matview_mdl.sql_view_definition,
                  'view_name': cls.demo_matview_mdl.sql_view_name,
                  'matview_name': cls.demo_matview_mdl.sql_mat_view_name,
                  'pg_version': 90205,
                  'state': 'nonexistent'
                  }
        cls.matview_id = cls.matview_mdl.create(values).id

    def test_simple_case(self):
        """Test some simple case, create/read/write/unlink"""
        users_mdl_id = self.env['ir.model'].search(
            [('model', '=', 'res.users')]).ids[0]
        values = {'name': u"Test",
                  'model_id': users_mdl_id,
                  'sql_definition': 'SELECT 1',
                  'view_name': u'test_view',
                  'matview_name': 'test_mat_view_name',
                  'pg_version': 90305,
                  'last_refresh_start_date': datetime.now(),
                  'last_refresh_end_date': datetime.now(),
                  }
        rec = self.matview_mdl.create(values)
        rec.write({'name': u"Fake test"})
        values.update({'name': u"Fake test",
                       'state': u'nonexistent',
                       })
        # don't wan't to get headheak to fix format date here
        values.pop('last_refresh_start_date')
        values.pop('last_refresh_end_date')
        self.assertRecord('materialized.sql.view', rec.id, values)
        rec.unlink()

    def test_launch_refresh_materialized_sql_view(self):
        mat_mdl = self.matview_mdl
        group = self.env.ref('base.group_user')
        demo_matview = self.demo_matview_mdl.browse(group.id)
        user_count = demo_matview.user_count
        self.users_mdl.create({'name': u"Test user",
                               'login': u"ttt",
                               'company_id': self.ref('base.main_company'),
                               'customer': False,
                               'email': 'demo@yourcompany.example.com',
                               'street': u"Avenue des Choux",
                               'city': u"Namue",
                               'zip': '5101',
                               'country_id': self.ref('base.be'),
                               })
        self.assertEquals(
            demo_matview.read(['user_count'])[0]['user_count'],
            user_count
        )
        recs = mat_mdl.search(
            [('matview_name', '=', self.demo_matview_mdl._sql_mat_view_name)]
        )
        recs.launch_refresh_materialized_sql_view()
        self.assertEquals(
            demo_matview.read(['user_count'])[0]['user_count'],
            user_count + 1
        )
        for rec in recs:
            self.assertEquals(rec.state, 'refreshed')

    def test_launch_refresh_materialized_sql_view_by_name(self):
        mat_mdl = self.matview_mdl
        group = self.env.ref('base.group_user')
        demo_matview = self.demo_matview_mdl.browse(group.id)
        user_count = demo_matview.user_count
        self.users_mdl.create(
            {'name': u"Test user2",
             'login': u"test2",
             'company_id': self.env.ref('base.main_company').id,
             'customer': False,
             'email': 'demo@yourcompany.example.com',
             'street': u"Avenue des Choux",
             'city': u"Namue",
             'zip': '5101',
             'country_id': self.ref('base.be'),
             })
        self.assertEquals(
            demo_matview.read(['user_count'])[0]['user_count'],
            user_count)
        mat_mdl.refresh_materialized_view_by_name(
            self.demo_matview_mdl._sql_mat_view_name)
        mat_views = mat_mdl.search(
            [('matview_name', '=', self.demo_matview_mdl._sql_mat_view_name)]
        )
        for mat_view in mat_views:
            self.assertEquals(mat_view.state, 'refreshed')
        # Read user count, there is one more now!
        self.assertEquals(
            demo_matview.read(['user_count'])[0]['user_count'],
            user_count + 1)

    def test_before_create_view(self):
        self.matview_mdl.before_create_view(dict(
            view_name=self.demo_matview_mdl._sql_mat_view_name))
        rec = self.matview_mdl.browse(self.matview_id)
        self.assertEquals((rec.state, rec.last_error_message),
                          ('creating', u""))

    def test_before_refresh_view(self):
        self.matview_mdl.before_refresh_view(dict(
            view_name=self.demo_matview_mdl._sql_mat_view_name))
        rec = self.matview_mdl.browse(self.matview_id)
        self.assertEquals((rec.state, rec.last_error_message),
                          ('refreshing', u""))

    def test_after_refresh_view(self):
        self.matview_mdl.after_refresh_view(dict(
            view_name=self.demo_matview_mdl._sql_mat_view_name))
        rec = self.matview_mdl.browse(self.matview_id)
        self.assertEquals((rec.state, rec.last_error_message),
                          ('refreshed', u""))

    def test_after_drop_view(self):
        self.matview_mdl.after_drop_view(dict(
            view_name=self.demo_matview_mdl._sql_mat_view_name))
        rec = self.matview_mdl.browse(self.matview_id)
        self.assertEquals((rec.state, rec.last_error_message),
                          ('nonexistent', u"last_error_message"))

    def test_aborted_matview(self):
        self.matview_mdl.with_context(
            {'error_message': u"Error details"}).aborted_matview(
                self.demo_matview_mdl._sql_mat_view_name)
        rec = self.matview_mdl.browse(self.matview_id)
        self.assertEquals((rec.state, rec.last_error_message),
                          ('aborted', u"Error details"))

    def test_create_if_not_exist(self):
        count = self.matview_mdl.search_count(
            [('view_name', '=', 'test_123')])
        self.matview_mdl.create_if_not_exist(
            {'model_name': self.demo_matview_mdl._name,
             'sql_definition': 'SELECT 1',
             'view_name': 'test_123',
             'matview_name': 'test_123_view',
             'pg_version': self.env.cr._cnx.server_version,
             })
        self.assertEquals(
            count + 1,
            self.matview_mdl.search_count(
                [('view_name', '=', 'test_123')])
        )
        self.matview_mdl.create_if_not_exist(
            {'model_name': self.demo_matview_mdl._name,
             'sql_definition': 'SELECT 1',
             'view_name': 'test_123',
             'matview_name': 'test_123_view',
             'pg_version': self.env.cr._cnx.server_version,
             })
        self.assertEquals(
            count + 1,
            self.matview_mdl.search_count(
                [('view_name', '=', 'test_123')])
        )
        self.matview_mdl.create_if_not_exist(
            {'model_name': self.demo_matview_mdl._name,
             'sql_definition': 'SELECT 1',
             'view_name': 'test_123',
             'matview_name': 'test_123_view',
             'pg_version': 90402,
             })
        self.assertEquals(
            count + 1,
            self.matview_mdl.search_count(
                [('view_name', '=', 'test_123')])
        )
