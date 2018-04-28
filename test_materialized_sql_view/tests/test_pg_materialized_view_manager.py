# -*- coding: utf-8 -*-
# Copyright 2016 Pierre Verkest <pverkest@anybox.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.tests.common import SingleTransactionCase
from openerp.addons.materialized_sql_view.model.abstract_materialized_sql_view import PGMaterializedViewManager  # noqa
from openerp.addons.materialized_sql_view.model.abstract_materialized_sql_view import PGNoMaterializedViewSupport  # noqa
from openerp.addons.materialized_sql_view.model.abstract_materialized_sql_view import PG090300  # noqa
import psycopg2


class PGMaterializedViewManagerTester(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(PGMaterializedViewManagerTester, cls).setUpClass()
        cls.users_mdl = cls.registry('res.users')
        cls.pg_manager = PGMaterializedViewManager
        cls.sql = 'SELECT * FROM res_users'
        cls.view_name = "test_view"
        cls.mat_view_name = "test_mat_view"

    def test_get_instance(self):
        self.assertIsInstance(
            self.pg_manager.getInstance(90299), PGNoMaterializedViewSupport)
        self.assertIsInstance(self.pg_manager.getInstance(90300), PG090300)
        self.assertIsInstance(self.pg_manager.getInstance(90301), PG090300)
        self.assertIsInstance(self.pg_manager.getInstance(90400), PG090300)

    def test_materialized_view(self):
        pg_versions = [self.cr._cnx.server_version]
        if self.cr._cnx.server_version >= 90300:
            # insert before, to test raise exception on the current version
            pg_versions.insert(0, 90200)

        for version in pg_versions:
            pg = self.pg_manager.getInstance(self.cr._cnx.server_version)
            pg.create_mat_view(
                self.cr, self.sql, self.view_name, self.mat_view_name)
            self.cr.execute('SELECT count(*) FROM %(mat_view)s' %
                            dict(mat_view=self.mat_view_name))
            initCount = self.cr.fetchone()[0]
            self.users_mdl.create(self.cr, self.uid,
                                  {'name': u"Test user",
                                   'login': u"ttt" + str(version),
                                   'company_id': self.ref('base.main_company'),
                                   'customer': False,
                                   'email': 'demo@yourcompany.example.com',
                                   'street': u"Avenue des Dessus-de-Lives, 2",
                                   'city': u"Namue",
                                   'zip': '5101',
                                   'country_id': self.ref('base.be'), },)
            self.cr.execute('SELECT count(*) FROM %(mat_view)s' %
                            dict(mat_view=self.mat_view_name))
            self.assertEquals(initCount, self.cr.fetchone()[0])
            pg.refresh_mat_view(self.cr, self.view_name, self.mat_view_name)
            self.cr.execute('SELECT count(*) FROM %(mat_view)s' %
                            dict(mat_view=self.mat_view_name))
            self.assertEquals(initCount + 1, self.cr.fetchone()[0])
            pg.drop_mat_view(self.cr, self.view_name, self.mat_view_name)
        # Test this only on the last db, because cursor will be broken
        self.assertRaises(psycopg2.Error, self.cr.execute,
                          'SELECT count(*) FROM %(mat_view)s' %
                          dict(mat_view=self.mat_view_name)
                          )

    def test_is_existed_relation(self):
        pg = self.pg_manager.getInstance(self.cr._cnx.server_version)
        pg.create_mat_view(self.cr, self.sql, self.view_name,
                           self.mat_view_name)
        self.assertTrue(pg.is_existed_relation(self.cr, self.view_name))
        self.assertTrue(pg.is_existed_relation(self.cr, self.view_name))
        pg.drop_mat_view(self.cr, self.view_name, self.mat_view_name)
        self.assertFalse(pg.is_existed_relation(self.cr, self.view_name))
        self.assertFalse(pg.is_existed_relation(self.cr, self.view_name))
