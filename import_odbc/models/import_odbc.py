# -*- coding: utf-8 -*-
# Copyright <2011> <Daniel Reis>
# Copyright <2017> <Jesus Ramiro>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
import sys
import logging
from datetime import datetime
from odoo import api, models, fields

_logger = logging.getLogger(__name__)
_loglvl = _logger.getEffectiveLevel()


class ImportOdbcDbtable(models.Model):
    _name = "import.odbc.dbtable"
    _description = 'Import Table Data'
    _order = 'exec_order'

    name = fields.Char(string='Datasource name', required=True, size=64)
    enabled = fields.Boolean(string='Execution enabled', default=True)
    dbsource_id = fields.Many2one('base.external.dbsource',
                                  string='Database source', required=True)
    sql_source = fields.Text(string='SQL', required=True,
                             help='Column names must be valid \
                             "import_data" columns.')
    model_target = fields. Many2one('ir.model', string='Target object')
    noupdate = fields.Boolean(string='No updates',
                              help="Only create new records;\
                              disable updates to existing records.")
    exec_order = fields.Integer(string='Execution order', default=10,
                                help="Defines the order to perform \
                                the import")
    last_sync = fields.Datetime(string='Last sync date',
                                help="Datetime for the last succesfull \
                                sync. \nLater changes on the source may \
                                not be replicated on the destination")
    start_run = fields.Datetime(string='Time started', readonly=True)
    last_run = fields.Datetime(string='Time ended', readonly=True)
    last_record_count = fields.Integer(string='Last record count',
                                       readonly=True)
    last_error_count = fields.Integer(string='Last error count', readonly=True)
    last_warn_count = fields.Integer(string='Last warning count', readonly=True)
    last_log = fields.Text(string='Last run log', readonly=True)
    ignore_rel_errors = fields.Boolean(string='Ignore relationship errors',
                                       help="On error try to reimport \
                                       rows ignoring relationships.")
    raise_import_errors = fields.Boolean(
        string='Raise import errors',
        help="Import errors not handled, intended for debugging purposes. "\
             "Also forces debug messages to be written to the server log."
    )

    @api.multi
    def _import_data(self, flds, data, model_obj, table_obj, log):
        """Import data and returns error msg or empty string"""

        def find_m2o(field_list):
            """"Find index of first column with a one2many field"""
            for i, x in enumerate(field_list):
                if len(x) > 3 and x[-3:] == ':id' or x[-3:] == '/id':
                    return i
            return -1

        def append_to_log(log, level, obj_id='', msg='', rel_id=''):
            if '_id_' in obj_id:
                obj_id = ('.'.join(obj_id.split('_')[:-2]) + ': ' +
                          obj_id.split('_')[-1])
            if ': .' in msg and not rel_id:
                rel_id = msg[msg.find(': .')+3:]
                if '_id_' in rel_id:
                    rel_id = ('.'.join(rel_id.split('_')[:-2]) +
                              ': ' + rel_id.split('_')[-1])
                    msg = msg[:msg.find(': .')]
            log['last_log'].append('%s|%s\t|%s\t|%s' % (level.ljust(5),
                                   obj_id, rel_id, msg))
        _logger.debug(data)
        cols = list(flds)  # copy to avoid side effects
        errmsg = str()

        model_obj = model_obj.with_context(noupdate=table_obj.noupdate)
        if table_obj.raise_import_errors:
            model_obj.load(cols, [data])
        else:
            try:
                model_obj.load(cols, [data])
            except:
                errmsg = str(sys.exc_info()[1])
        if errmsg and not table_obj.ignore_rel_errors:
            # Fail
            append_to_log(log, 'ERROR', data, errmsg)
            log['last_error_count'] += 1
            return False
        if errmsg and table_obj.ignore_rel_errors:
            # Warn and retry ignoring many2one fields...
            append_to_log(log, 'WARN', data, errmsg)
            log['last_warn_count'] += 1
            # Try ignoring each many2one
            # (tip: in the SQL sentence select more problematic FKs first)
            i = find_m2o(cols)
            if i >= 0:
                # Try again without the [i] column
                del cols[i]
                del data[i]
                self._import_data(cols, data, model_obj,
                                  table_obj, log)
            else:
                # Fail
                append_to_log(log, 'ERROR', data,
                              'Removed all m2o keys and still fails.')
                log['last_error_count'] += 1
                return False
        return True

    @api.multi
    def import_run(self, ids=None):
        if not self._ids and ids:
            self._ids = ids
        actions = self.read(['id', 'exec_order'])
        actions.sort(key=lambda x: (x['exec_order'], x['id']))

        # Consider each dbtable:
        for action_ref in actions:
            obj = self.browse(action_ref['id'])
            db_model = \
                self.env['base.external.dbsource'].browse(obj.dbsource_id.id)
            if not obj.enabled:
                continue  # skip

            _logger.setLevel(obj.raise_import_errors and
                             logging.DEBUG or _loglvl)
            _logger.debug('Importing %s...' % obj.name)

            # now() microseconds are stripped
            # to avoid problem with SQL smalldate
            model_name = obj.model_target.model
            model_obj = self.env[model_name]
            xml_prefix = '__import__.' + model_name.replace('.', '_') + '_'
            log = {'start_run': datetime.now().replace(microsecond=0),
                   'last_run': None,
                   'last_record_count': 0,
                   'last_error_count': 0,
                   'last_warn_count': 0,
                   'last_log': list()}
            obj.write(log)

            # Prepare SQL sentence; replace "%s" with the last_sync date
            if obj.last_sync:
                sync = datetime.strptime(obj.last_sync, "%Y-%m-%d %H:%M:%S")
            else:
                sync = datetime(1900, 1, 1, 0, 0, 0)
            params = [(sync)]
            res = db_model.execute(obj.sql_source, params, metadata=True)

            # Exclude columns titled "None"; add (xml_)"id" column
            cidx = ([i for i, x in enumerate(res['cols'])
                     if x.upper() != 'NONE'])
            cols = ([x for i, x in enumerate(res['cols'])
                     if x.upper() != 'NONE'] + ['id'])

            # Import each row:
            for row in res['rows']:
                # Build data row;
                # import only columns present in the "cols" list
                data = list()
                for i in cidx:
                    v = row[i]
                    if isinstance(v, str):
                        v = v.strip()
                    data.append(v)
                data.append(xml_prefix + str(row[0]).strip())
                # Import the row; on error, write line to the log
                log['last_record_count'] += 1
                self._import_data(cols, data, model_obj, obj, log)
                if log['last_record_count'] % 500 == 0:
                    _logger.info('...%s rows processed...'
                                 % (log['last_record_count']))

            # Finished importing all rows
            # If no errors, write new sync date
            if not (log['last_error_count'] or log['last_warn_count']):
                log['last_sync'] = log['start_run']
            level = logging.DEBUG
            if log['last_warn_count']:
                level = logging.WARN
            if log['last_error_count']:
                level = logging.ERROR
            _logger.log(level,
                        'Imported %s , %d rows, %d errors, %d warnings.' %
                        (model_name, log['last_record_count'],
                         log['last_error_count'],
                         log['last_warn_count']))
            # Write run log, either if the table import is active or inactive
            if log['last_log']:
                log['last_log'].insert(0,
                                       'LEVEL|== Line ==    |== Relationship \
                                       ==|== Message ==')
            log.update({'last_log': '\n'.join(log['last_log'])})
            log.update({'last_run': datetime.now().replace(microsecond=0)})
            obj.write(log)

        # Finished
        _logger.debug('Import job FINISHED.')
        return True

    @api.multi
    def import_schedule(self):
        cron_obj = self.env['ir.cron']
        new_create_cron = cron_obj.create({
            'name': 'Import ODBC tables',
            'interval_type': 'hours',
            'interval_number': 24,
            'numbercall': -1,
            'doall': False,
            'active': True,
            'args' : '[(%s,)]' % (self.id),
            'model': 'import.odbc.dbtable',
            'function': 'import_run'
            })
        return {
            'name': 'Import ODBC tables',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'ir.cron',
            'res_id': new_create_cron.id,
            'type': 'ir.actions.act_window'
            }
