# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
from datetime import datetime
from openerp import SUPERUSER_ID
from openerp.tools.translate import _

MATERIALIZED_SQL_VIEW_STATES = [('nonexistent', _('Nonexistent')),
                                ('creating', _('Creating')),
                                ('refreshing', _('Refreshing')),
                                ('refreshed', _('Refreshed')),
                                ('aborted', _('Aborted')),
                                ]


class MaterializedSqlView(orm.Model):
    _name = 'materialized.sql.view'
    _description = u"Materialized SQL View"

    _columns = {
        'name': fields.char('Name', required=True),
        'model_id': fields.many2one(
            'ir.model', 'Model', required=True, delete='cascade',
            readonly=True),
        'view_name': fields.char(
            'SQL view name', required=True, readonly=True),
        'matview_name': fields.char(
            'Materialized SQL View Name', required=True, readonly=True),
        'pg_version': fields.integer(
            'Mat view pg version', required=True, readonly=True),
        'sql_definition': fields.text('sql', required=True, readonly=True),
        'last_refresh_start_date': fields.datetime(
            'Last refreshed start date', readonly=True),
        'last_refresh_end_date': fields.datetime(
            'Last refreshed end date', readonly=True),
        'last_error_message': fields.text(
            'Last error', readonly=True),
        'state': fields.selection(
            MATERIALIZED_SQL_VIEW_STATES, 'State', required=True,
            readonly=True)}

    _defaults = {
        'state': 'nonexistent',
    }

    def launch_refresh_materialized_sql_view(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        # by default, refresh materialized view is done ascynchronously
        # this is used to give the hand back to the user when he click
        # on refresh button. Some other cases like utest needs to run it
        # scynchronously
        if context.get('ascyn', True):
            self.schedul_refresh_materialized_sql_view(cr, uid, ids, context)
            return self.write(cr, uid, ids, {'state': 'refreshing'},
                              context=context)
        else:
            return self.refresh_materialized_view(cr, uid, ids, context)

    def schedul_refresh_materialized_sql_view(
        self, cr, uid, ids, context=None
    ):
        if not context:
            context = {}
        vals = {
            'name': _(u"Refresh materialized views"),
            'user_id': uid,
            'priority': 100,
            'numbercall': 1,
            'doall': True,
            'model': self._name,
            'function': 'refresh_materialized_view',
            'args': repr((ids, context)),
        }
        self.pool.get('ir.cron').create(
            cr, SUPERUSER_ID, vals, context=context)

    def refresh_materialized_view_by_name(self, cr, uid, mat_view_name='',
                                          context=None):
        ids = self.search_materialized_sql_view_ids_from_matview_name(
            cr, uid, mat_view_name, context=context)
        return self.refresh_materialized_view(cr, uid, ids, context=context)

    def refresh_materialized_view(self, cr, uid, ids, context=None):
        result = []
        matviews_performed = []
        ir_model = self.pool.get('ir.model')
        for matview in self.read(cr, uid, ids,
                                 ['id', 'model_id', 'matview_name'],
                                 context=context, load='_classic_write'):
            if matview['matview_name'] in matviews_performed:
                continue
            model = ir_model.read(
                cr, uid, matview['model_id'], ['model'],
                context=context)['model']
            matview_mdl = self.pool.get(model)
            result.append(
                matview_mdl.refresh_materialized_view(
                    cr,
                    uid,
                    context=context))
            matviews_performed.append(matview['matview_name'])
        return result

    def create_if_not_exist(self, cr, uid, values, context=None):
        if self.search(cr, uid, [('model_id.model', '=', values['model_name']),
                                 ('view_name', '=', values['view_name']),
                                 ('matview_name', '=', values['matview_name']),
                                 ], context=context, count=True) == 0:
            ir_mdl = self.pool.get('ir.model')
            model_id = ir_mdl.search(cr, uid,
                                     [('model', '=', values['model_name']), ],
                                     context=context)
            values.update({'model_id': model_id[0]})
            if not values.get('name'):
                name = ir_mdl.read(
                    cr, uid, model_id, ['name'], context=context)[0]['name']
                values.update({'name': name})
            values.pop('model_name')
            self.create(cr, uid, values, context=context)

    def search_materialized_sql_view_ids_from_matview_name(
            self, cr, uid, matview_name, context=None):
        return self.search(cr, uid,
                           [('matview_name', '=', matview_name)],
                           context=context)

    def before_create_view(self, cr, uid, matview_name, context=None):
        return self.write_values(cr, uid, matview_name,
                                 {'last_refresh_start_date': datetime.now(),
                                  'state': 'creating',
                                  'last_error_message': '',
                                  }, context=context)

    def before_refresh_view(self, cr, uid, matview_name, context=None):
        return self.write_values(cr, uid, matview_name,
                                 {'last_refresh_start_date': datetime.now(),
                                  'state': 'refreshing',
                                  'last_error_message': '',
                                  }, context=context)

    def after_refresh_view(self, cr, uid, matview_name, context=None):
        values = {'last_refresh_end_date': datetime.now(),
                  'state': 'refreshed',
                  'last_error_message': '',
                  }
        pg_version = cr._cnx.server_version
        if context.get('values'):
            vals = context.get('values')
            pg_version = vals.get('pg_version', pg_version)
            if vals.get('sql_definition'):
                values.update({'sql_definition': vals.get('sql_definition')})
            if vals.get('view_name'):
                values.update({'view_name': vals.get('view_name')})
        values.update({'pg_version': pg_version})
        return self.write_values(
            cr,
            uid,
            matview_name,
            values,
            context=context)

    def after_drop_view(self, cr, uid, matview_name, context=None):
        # Do not unlink here, we don't want to use on other record when refresh
        # need to drop and create a new materialized view
        return self.write_values(cr, uid, matview_name,
                                 {'state': 'nonexistent',
                                  'last_error_message': '',
                                  }, context=context)

    def write_values(self, cr, uid, matview_name, values, context=None):
        ids = self.search_materialized_sql_view_ids_from_matview_name(
            cr, uid, matview_name, context=context)
        return self.write(cr, uid, ids, values, context=context)

    def aborted_matview(self, cr, uid, matview_name, context=None):
        if not context:
            context = {}
        return self.write_values(cr, uid, matview_name,
                                 {'state': 'aborted',
                                  'last_refresh_end_date': datetime.now(),
                                  'last_error_message':
                                  context.get('error_message',
                                              'Error not difined')
                                  }, context=context)
