# -*- coding: utf-8 -*-
# Copyright 2016 Pierre Verkest <pverkest@anybox.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import psycopg2
import logging
from openerp import api, models
from openerp.exceptions import except_orm
from openerp import SUPERUSER_ID
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)
ABSTRACT_MODEL_NAME = 'abstract.materialized.sql.view'


class AbstractMaterializedSqlView(models.AbstractModel):

    """This class is an abstract model to help developer to
       create/refresh/update materialized view.
    """
    _name = ABSTRACT_MODEL_NAME
    _description = u"This is an helper class to manage materialized SQL view"
    _auto = False

    _sql_mat_view_name = None
    """The name of the materialized sql view.
       Must be defined in inherit class (using inherit = [])
    """

    @property
    def sql_mat_view_name(self):
        if not self._sql_mat_view_name:
            self._sql_mat_view_name = self._table
        return self._sql_mat_view_name

    _sql_view_name = None
    """The name of the sql view used to generate the materialized view
       Must be defined in inherit class (using inherit = [])
    """

    @property
    def sql_view_name(self):
        if not self._sql_view_name:
            self._sql_view_name = self._table + '_view'
        return self._sql_view_name

    _sql_view_definition = None
    """The sql query to generate the view (without any create views)
    """

    @property
    def sql_view_definition(self):
        if not self._sql_view_definition:
            raise ValueError(u"Properties must be defined in subclass",
                             u"_sql_view_definition properties should be "
                             u"redifined in sub class"
                             )
        return self._sql_view_definition

    def init(self, cr):
        """Init method is called when installing or updating the module.
           Check if the sql changed, and refresh materialized view only if
           needs.
        """
        if hasattr(super(AbstractMaterializedSqlView, self), 'init'):
            super(self, AbstractMaterializedSqlView).init(cr)

        # prevent against Abstract class initialization
        if self._name == ABSTRACT_MODEL_NAME:
            return

        logger.info(u"Init materialized view, using Postgresql %r",
                    cr._cnx.server_version)
        self.create_or_upgrade_pg_matview_if_needs(cr, SUPERUSER_ID)

    @api.model
    def create_materialized_view(self):
        context, cr = self.env.context, self.env.cr
        if not context:
            context = {}
        result = []
        logger.info("Create Materialized view %r", self.sql_mat_view_name)
        pg_version = context.get('force_pg_version',
                                 cr._cnx.server_version)
        self.change_matview_state('before_create_view', pg_version)
        try:
            pg = PGMaterializedViewManager.getInstance(pg_version)
            # make sure there is no existing views create uppon the same
            # version this could be possible if materialized.sql.view entry is
            # deleted.
            # TODO: maybe move it in create_or_upgrade_pg_matview_if_needs and
            # automaticly detect if it's a mat view or a table cf utests
            pg.drop_mat_view(cr, self.sql_view_name, self.sql_mat_view_name)
            self.before_create_materialized_view()
            pg.create_mat_view(cr, self.sql_view_definition,
                               self.sql_view_name, self.sql_mat_view_name)
            self.after_create_materialized_view()
        except psycopg2.Error as e:
            self.report_sql_error(e, pg_version)
        else:
            result = self.change_matview_state(
                'after_refresh_view', pg_version
            )
        return result

    @api.model
    def refresh_materialized_view(self):
        context, cr = self.env.context, self.env.cr
        result = self.create_or_upgrade_pg_matview_if_needs()
        if not result:
            logger.info(
                "Refresh Materialized view %r", self.sql_mat_view_name)
            if not context:
                context = {}
            pg_version = context.get(
                'force_pg_version', cr._cnx.server_version)
            self.change_matview_state('before_refresh_view', pg_version)
            try:
                self.before_refresh_materialized_view()
                pg = PGMaterializedViewManager.getInstance(pg_version)
                pg.refresh_mat_view(
                    cr, self.sql_view_name, self.sql_mat_view_name)
                self.after_refresh_materialized_view()
            except psycopg2.Error as e:
                self.report_sql_error(e, pg_version)
            else:
                result = self.change_matview_state('after_refresh_view',
                                                   pg_version)
        return result

    @api.model
    def create_or_upgrade_pg_matview_if_needs(self):
        """Compare everything that can cause the needs to drop and recreate
           materialized view. Return True if something done.
        """
        context, cr = self.env.context, self.env.cr
        if not context:
            context = {}
        mat_sql_views = self.env['materialized.sql.view'].search(
            [('matview_name', '=', self.sql_mat_view_name)]
        )
        if len(mat_sql_views):
            # As far matview_mdl is refered by its view name, to get one or
            # more instance is technicly the same.
            mat_sql_views = mat_sql_views[0]
            pg_version = context.get(
                'force_pg_version', cr._cnx.server_version
            )
            pg = PGMaterializedViewManager.getInstance(cr._cnx.server_version)
            if (
                mat_sql_views.pg_version != pg_version or
                mat_sql_views.sql_definition != self.sql_view_definition or
                mat_sql_views.view_name != self.sql_view_name or
                mat_sql_views.state in ['nonexistent', 'aborted'] or
                not pg.is_existed_relation(cr, self.sql_view_name) or
                not pg.is_existed_relation(cr, self.sql_mat_view_name)
            ):
                self.drop_materialized_view_if_exist(
                    mat_sql_views.pg_version,
                    view_name=mat_sql_views.view_name
                )
            else:
                return []
        return self.create_materialized_view()

    @api.model
    def change_matview_state(self, method_name, pg_version):
        matview_mdl = self.env['materialized.sql.view']
        # Make sure object exist or create it
        values = {
            'model_name': self._name,
            'view_name': self.sql_view_name,
            'matview_name': self.sql_mat_view_name,
            'sql_definition': self.sql_view_definition,
            'pg_version': pg_version,
        }
        matview_mdl.create_if_not_exist(values)
        method = getattr(matview_mdl, method_name)
        return method(values)

    @api.model
    def drop_materialized_view_if_exist(self, pg_version, view_name=None,
                                        mat_view_name=None):
        cr = self.env.cr
        result = []
        logger.info("Drop Materialized view %r", self.sql_mat_view_name)
        try:
            self.before_drop_materialized_view()
            pg = PGMaterializedViewManager.getInstance(pg_version)
            if not view_name:
                view_name = self.sql_view_name
            if not mat_view_name:
                mat_view_name = self.sql_mat_view_name
            pg.drop_mat_view(cr, view_name, mat_view_name)
            self.after_drop_materialized_view()
        except psycopg2.Error as e:
            self.report_sql_error(e, pg_version)
        else:
            result = self.change_matview_state('after_drop_view',
                                               pg_version)
        return result

    @api.model
    def report_sql_error(self, err, pg_version):
        context, cr = self.env.context, self.env.cr
        if not context:
            context = {}
        context = {'error_message': err.pgerror}
        cr.rollback()
        self.with_context(context).change_matview_state(
            'aborted_matview', pg_version)

    @api.model
    def before_drop_materialized_view(self):
        """Method called before drop materialized view and view,
           Nothing done in abstract method, it's  hook to used in subclass
        """

    @api.model
    def after_drop_materialized_view(self):
        """Method called after drop materialized view and view,
           Nothing done in abstract method, it's  hook to used in subclass
        """

    @api.model
    def before_create_materialized_view(self):
        """Method called before create materialized view and view,
           Nothing done in abstract method, it's  hook to used in subclass
        """

    @api.model
    def after_create_materialized_view(self):
        """Method called after create materialized view and view,
           Nothing done in abstract method, it's  hook to used in subclass
        """

    @api.model
    def before_refresh_materialized_view(self):
        """Method called before refresh materialized view,
           this was made to do things like drop index before in the same
           transaction.

           Nothing done in abstract method, it's  hook to used in subclass
        """

    @api.model
    def after_refresh_materialized_view(self):
        """Method called after refresh materialized view,
           this was made to do things like add index after refresh data

           Nothing done in abstract method, it's  hook to used in subclass
        """

    @api.multi
    def write(self, vals):
        raise except_orm(u"Write on materialized view is forbidden",
                         u"Write on materialized view is forbidden,"
                         u"because data would be lost at the next refresh"
                         )

    @api.multi
    def create(self, vals):
        raise except_orm(u"Create data on materialized view is forbidden",
                         u"Create data on materialized view is forbidden,"
                         u"because data would be lost at the next refresh"
                         )

    @api.multi
    def unlink(self):
        raise except_orm(u"Remove data on materialized view is forbidden",
                         u"Remove data on materialized view is forbidden,"
                         u"because data would be lost at the next refresh"
                         )


class PGMaterializedViewManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_mat_view(self, cr, sql, view_name, mat_view_name):
        """Abstract Method to overwrite in subclass to create sql view
           and materialized sql view from sql query.
        """

    @abstractmethod
    def refresh_mat_view(self, cr, view_name, mat_view_name):
        """Abstract Method  to overwrite in subclass to refresh
           materialized sql view
        """

    @abstractmethod
    def drop_mat_view(self, cr, view_name, mat_view_name):
        """Abstract Method to overwrite in subclass to drop materialized view
           and clean every thing to its authority
        """

    def is_existed_relation(self, cr, relname):
        cr.execute(
            "select count(*) from pg_class where relname like '%(relname)s'" %
            {'relname': relname})
        return cr.fetchone()[0] > 0

    @classmethod
    def getInstance(cls, version):
        """Method that return the class depending pg server_version
        """
        if version >= 90300:
            return PG090300()
        else:
            return PGNoMaterializedViewSupport()


class PGNoMaterializedViewSupport(PGMaterializedViewManager):

    def create_mat_view(self, cr, sql, view_name, mat_view_name):
        cr.execute("CREATE VIEW %(view_name)s AS (%(sql)s)" %
                   dict(view_name=view_name, sql=sql, ))
        cr.execute("CREATE TABLE %(mat_view_name)s "
                   "AS SELECT * FROM %(view_name)s" %
                   dict(mat_view_name=mat_view_name,
                        view_name=view_name,
                        ))

    def refresh_mat_view(self, cr, view_name, mat_view_name):
        cr.execute("DELETE FROM %(mat_view_name)s" %
                   dict(mat_view_name=mat_view_name,
                        ))
        cr.execute(
            "INSERT INTO %(mat_view_name)s SELECT * FROM %(view_name)s" %
            dict(
                mat_view_name=mat_view_name,
                view_name=view_name,
            ))

    def drop_mat_view(self, cr, view_name, mat_view_name):
        cr.execute("DROP TABLE IF EXISTS %s" % (mat_view_name))
        cr.execute("DROP VIEW IF EXISTS %s" % (view_name,))


class PG090300(PGMaterializedViewManager):

    def create_mat_view(self, cr, sql, view_name, mat_view_name):
        cr.execute("CREATE VIEW %(view_name)s AS (%(sql)s)" %
                   dict(view_name=view_name, sql=sql, ))
        cr.execute("CREATE MATERIALIZED VIEW %(mat_view_name)s AS "
                   "SELECT * FROM %(view_name)s" %
                   dict(mat_view_name=mat_view_name,
                        view_name=view_name,
                        ))

    def refresh_mat_view(self, cr, view_name, mat_view_name):
        cr.execute("REFRESH MATERIALIZED VIEW %(mat_view_name)s" %
                   dict(mat_view_name=mat_view_name,
                        ))

    def drop_mat_view(self, cr, view_name, mat_view_name):
        cr.execute("DROP MATERIALIZED VIEW IF EXISTS %s" %
                   (mat_view_name))
        cr.execute("DROP VIEW IF EXISTS %s" % (view_name,))
