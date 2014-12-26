from anybox.testing.openerp import TransactionCase


class NonTransactionalCase(TransactionCase):

    def setUp(self):
        super(NonTransactionalCase, self).setUp()
        self.demo_matview_mdl = self.registry('test.materialized.view')
        self.mat_view_mdl = self.registry('materialized.sql.view')
        self.context = {'ascyn': False}

    def test_overload_before_refresh(self):
        demo, mat_mdl = self.demo_matview_mdl, self.demo_matview_mdl
        save_method = self.demo_matview_mdl.before_refresh_materialized_view

        def before_refresh_materialized_view(cr, uid, context=None):
            cr.execute("test")

        cr, uid = self.cr, self.uid
        demo.before_refresh_materialized_view = before_refresh_materialized_view  # noqa
        self.demo_matview_mdl.refresh_materialized_view(
            cr, uid, context=self.context)
        self.demo_matview_mdl.before_refresh_materialized_view = save_method
        ids = mat_mdl.search_materialized_sql_view_ids_from_matview_name(
            cr, uid, self.demo_matview_mdl._sql_mat_view_name,
            context=self.context)
        self.assertEqual(
            self.mat_view_mdl.read(
                cr, uid, ids, ['state'], context=self.context)[0]['state'],
            u'aborted')

    def test_overload_after_refresh(self):
        demo, mat_mdl = self.demo_matview_mdl, self.demo_matview_mdl
        save_method = demo.after_refresh_materialized_view

        def after_refresh_materialized_view(cr, uid, context=None):
            cr.execute("test")

        cr, uid = self.cr, self.uid
        demo.after_refresh_materialized_view = after_refresh_materialized_view
        self.demo_matview_mdl.refresh_materialized_view(
            cr, uid, context=self.context)
        self.demo_matview_mdl.after_refresh_materialized_view = save_method
        ids = mat_mdl.search_materialized_sql_view_ids_from_matview_name(
            cr, uid, demo._sql_mat_view_name, context=self.context)
        self.assertEqual(
            self.mat_view_mdl.read(
                cr, uid, ids, ['state'], context=self.context)[0]['state'],
            u'aborted')

    def test_overload_before_drop(self):
        demo, mat_mdl = self.demo_matview_mdl, self.demo_matview_mdl
        cr, uid = self.cr, self.uid
        save_method = self.demo_matview_mdl.before_drop_materialized_view

        def before_drop_materialized_view(cr, uid, context=None):
            cr.execute("test")

        demo.before_drop_materialized_view = before_drop_materialized_view
        demo.drop_materialized_view_if_exist(cr, uid,
                                             self.cr._cnx.server_version,
                                             context=self.context)
        self.demo_matview_mdl.before_drop_materialized_view = save_method
        ids = mat_mdl.search_materialized_sql_view_ids_from_matview_name(
            cr, uid, self.demo_matview_mdl._sql_mat_view_name,
            context=self.context)
        self.assertEqual(
            self.mat_view_mdl.read(
                cr, uid, ids, ['state'], context=self.context)[0]['state'],
            u'aborted')
        self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs(
            cr, uid, context=self.context)

    def test_overload_after_drop(self):
        demo, mat_mdl = self.demo_matview_mdl, self.demo_matview_mdl
        save_method = self.demo_matview_mdl.after_drop_materialized_view

        def after_drop_materialized_view(cr, uid, context=None):
            cr.execute("test")

        cr, uid = self.cr, self.uid
        demo.after_drop_materialized_view = after_drop_materialized_view
        demo.drop_materialized_view_if_exist(cr, uid,
                                             self.cr._cnx.server_version,
                                             context=self.context)
        self.demo_matview_mdl.after_drop_materialized_view = save_method
        ids = mat_mdl.search_materialized_sql_view_ids_from_matview_name(
            cr, uid, demo._sql_mat_view_name, context=self.context)
        self.assertEqual(
            self.mat_view_mdl.read(
                cr, uid, ids, ['state'], context=self.context)[0]['state'],
            u'aborted')
        self.demo_matview_mdl.create_or_upgrade_pg_matview_if_needs(
            cr, uid, context=self.context)

    def test_overload_before_create(self):
        demo, mat_mdl = self.demo_matview_mdl, self.demo_matview_mdl
        cr, uid = self.cr, self.uid
        demo.drop_materialized_view_if_exist(cr, uid,
                                             self.cr._cnx.server_version,
                                             context=self.context)
        save_method = self.demo_matview_mdl.before_create_materialized_view

        def before_create_materialized_view(cr, uid, context=None):
            cr.execute("test")

        demo.before_create_materialized_view = before_create_materialized_view
        self.demo_matview_mdl.create_materialized_view(
            cr, uid, context=self.context)
        self.demo_matview_mdl.before_create_materialized_view = save_method
        ids = mat_mdl.search_materialized_sql_view_ids_from_matview_name(
            cr, uid, demo._sql_mat_view_name, context=self.context)
        self.assertEqual(
            self.mat_view_mdl.read(
                cr, uid, ids, ['state'], context=self.context)[0]['state'],
            u'aborted')

    def test_overload_after_create(self):
        demo, mat_mdl = self.demo_matview_mdl, self.demo_matview_mdl
        cr, uid = self.cr, self.uid
        demo.drop_materialized_view_if_exist(cr, uid,
                                             self.cr._cnx.server_version,
                                             context=self.context)
        save_method = self.demo_matview_mdl.after_create_materialized_view

        def after_create_materialized_view(cr, uid, context=None):
            cr.execute("test")

        demo.after_create_materialized_view = after_create_materialized_view
        self.demo_matview_mdl.create_materialized_view(
            cr, uid, context=self.context)
        self.demo_matview_mdl.after_create_materialized_view = save_method
        ids = mat_mdl.search_materialized_sql_view_ids_from_matview_name(
            cr, uid, demo._sql_mat_view_name, context=self.context)
        self.assertEqual(
            self.mat_view_mdl.read(
                cr, uid, ids, ['state'], context=self.context)[0]['state'],
            u'aborted')
