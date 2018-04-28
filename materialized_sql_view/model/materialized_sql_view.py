# -*- coding: utf-8 -*-
# Copyright 2016 Pierre Verkest <pverkest@anybox.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models
from datetime import datetime


MATERIALIZED_SQL_VIEW_STATES = [('nonexistent', 'Nonexistent'),
                                ('creating', 'Creating'),
                                ('refreshing', 'Refreshing'),
                                ('refreshed', 'Refreshed'),
                                ('aborted', 'Aborted'),
                                ]


class MaterializedSqlView(models.Model):
    _name = 'materialized.sql.view'
    _description = u"Materialized SQL View"

    name = fields.Char('Name', required=True)
    model_id = fields.Many2one(comodel_name='ir.model', String='Model',
                               required=True, readonly=True)
    view_name = fields.Char('SQL view name', required=True, readonly=True)
    matview_name = fields.Char('Materialized SQL View Name', required=True,
                               readonly=True)
    pg_version = fields.Integer('Mat view pg version', required=True,
                                readonly=True)
    sql_definition = fields.Text('sql', required=True, readonly=True)
    last_refresh_start_date = fields.Datetime('Last refreshed start date',
                                              readonly=True)
    last_refresh_end_date = fields.Datetime('Last refreshed end date',
                                            readonly=True)
    last_error_message = fields.Text('Last error', readonly=True)
    state = fields.Selection(selection=MATERIALIZED_SQL_VIEW_STATES,
                             string='State', required=True, readonly=True,
                             default='nonexistent')

    @api.multi
    def launch_refresh_materialized_sql_view(self):
        context = self.env.context
        if not context:
            context = {}
        if context.get('ascyn', True):
            self.schedul_refresh_materialized_sql_view()
            return self.write({'state': 'refreshing'})
        else:
            return self.refresh_materialized_view()

    @api.multi
    def schedul_refresh_materialized_sql_view(self):
        context = self.env.context
        if not context:
            context = {}
        vals = {
            'name': u"Refresh materialized views",
            'user_id': self.env.uid,
            'priority': 100,
            'numbercall': 1,
            'doall': True,
            'model': self._name,
            'function': 'refresh_materialized_view',
            'args': repr((self.ids, context)),
        }
        self.env['ir.cron'].sudo().create(vals)

    @api.model
    def refresh_materialized_view_by_name(self, mat_view_name=None):
        records = self.search(
            [('matview_name', '=', 'mat_view_name')]
        )
        return records.refresh_materialized_view()

    @api.multi
    def refresh_materialized_view(self):
        result = []
        matviews_performed = []
        for matview in self:
            if matview.matview_name in matviews_performed:
                continue
            model = matview.model_id.model
            matview_mdl = self.env[model]
            result.append(matview_mdl.refresh_materialized_view())
            matviews_performed.append(matview.matview_name)
        return result

    @api.model
    def create_if_not_exist(self, values):
        if self.search_count(
            [
                ('model_id.model', '=', values['model_name']),
                ('view_name', '=', values['view_name']),
                ('matview_name', '=', values['matview_name']),
            ]
        ) == 0:
            ir_mdl = self.env['ir.model']
            model_ids = ir_mdl.search(
                [('model', '=', values['model_name'])]
            ).ids
            values.update({'model_id': model_ids[0]})
            if not values.get('name'):
                name = ir_mdl.browse(model_ids[0]).name
                values.update({'name': name})
            values.pop('model_name')
            self.create(values)

    @api.model
    def before_create_view(self, matview):
        return self.write_values(matview.get('view_name'),
                                 {'last_refresh_start_date': datetime.now(),
                                  'state': 'creating',
                                  'last_error_message': '',
                                  })

    @api.model
    def before_refresh_view(self, matview):
        return self.write_values(matview.get('view_name'),
                                 {'last_refresh_start_date': datetime.now(),
                                  'state': 'refreshing',
                                  'last_error_message': '',
                                  })

    @api.model
    def after_refresh_view(self, matview):
        values = {'last_refresh_end_date': datetime.now(),
                  'state': 'refreshed',
                  'last_error_message': '',
                  }
        pg_version = self.env.cr._cnx.server_version
        pg_version = matview.get('pg_version', pg_version)
        if matview.get('sql_definition'):
            values.update({'sql_definition': matview.get('sql_definition')})
        if matview.get('view_name'):
            values.update({'view_name': matview.get('view_name')})
        values.update({'pg_version': pg_version})
        return self.write_values(matview.get('matview_name'), values)

    @api.model
    def after_drop_view(self, matview):
        # Do not unlink here, we don't want to use on other record when refresh
        # need to drop and create a new materialized view
        return self.write_values(matview.get('view_name'),
                                 {'state': 'nonexistent',
                                  'last_error_message': '',
                                  })

    @api.model
    def write_values(self, matview_name, values):
        records = self.search([('matview_name', '=', matview_name)])
        return records.write(values)

    @api.model
    def aborted_matview(self, matview_name):
        context = self.env.context
        if not context:
            context = {}
        return self.write_values(matview_name,
                                 {'state': 'aborted',
                                  'last_refresh_end_date': datetime.now(),
                                  'last_error_message':
                                  context.get('error_message',
                                              'Error not difined')
                                  })
