
import base64
import logging
import os
import pstats
import re
import subprocess
import sys
from contextlib import contextmanager
from cProfile import Profile

import lxml.html
from psycopg2 import OperationalError, ProgrammingError

from odoo import _, api, exceptions, fields, models, sql_db, tools

if sys.version_info[0] >= 3:
    from io import StringIO as IO
else:
    from io import BytesIO as IO

DATETIME_FORMAT_FILE = "%Y%m%d_%H%M%S"
CPROFILE_EMPTY_CHARS = b"{0"
PGOPTIONS = {
    'log_min_duration_statement': '0',
    'client_min_messages': 'notice',
    'log_min_messages': 'warning',
    'log_min_error_statement': 'error',
    'log_duration': 'off',
    'log_error_verbosity': 'verbose',
    'log_lock_waits': 'on',
    'log_statement': 'none',
    'log_temp_files': '0',
}
PGOPTIONS_ENV = ' '.join(["-c %s=%s" % (param, value)
                          for param, value in PGOPTIONS.items()])
PY_STATS_FIELDS = [
    'ncalls',
    'tottime', 'tt_percall',
    'cumtime', 'ct_percall',
    'file', 'lineno', 'method',
]
LINE_STATS_RE = re.compile(
    r'(?P<%s>\d+/?\d+|\d+)\s+(?P<%s>\d+\.?\d+)\s+(?P<%s>\d+\.?\d+)\s+'
    r'(?P<%s>\d+\.?\d+)\s+(?P<%s>\d+\.?\d+)\s+(?P<%s>.*):(?P<%s>\d+)'
    r'\((?P<%s>.*)\)' % tuple(PY_STATS_FIELDS))

_logger = logging.getLogger(__name__)


class ProfilerProfilePythonLine(models.Model):
    _name = 'profiler.profile.python.line'
    _description = 'Profiler Python Line to save cProfiling results'
    _rec_name = 'cprof_fname'
    _order = 'cprof_cumtime DESC'

    profile_id = fields.Many2one('profiler.profile', required=True,
                                 ondelete='cascade')
    cprof_tottime = fields.Float("Total time")
    cprof_ncalls = fields.Float("Calls")
    cprof_nrcalls = fields.Float("Recursive Calls")
    cprof_ttpercall = fields.Float("Time per call")
    cprof_cumtime = fields.Float("Cumulative time")
    cprof_ctpercall = fields.Float("CT per call")
    cprof_fname = fields.Char("Filename:lineno(method)")


class ProfilerProfile(models.Model):
    _name = 'profiler.profile'
    _description = 'Profiler Profile'

    @api.model
    def _find_loggers_path(self):
        try:
            self.env.cr.execute("SHOW log_directory")
        except ProgrammingError:
            return
        log_directory = self.env.cr.fetchone()[0]
        self.env.cr.execute("SHOW log_filename")
        log_filename = self.env.cr.fetchone()[0]
        log_path = os.path.join(log_directory, log_filename)
        if not os.path.isabs(log_path):
            # It is relative path then join data_directory
            self.env.cr.execute("SHOW data_directory")
            data_dir = self.env.cr.fetchone()[0]
            log_path = os.path.join(data_dir, log_path)
        return log_path

    name = fields.Char(required=True)
    enable_python = fields.Boolean(default=True)
    enable_postgresql = fields.Boolean(
        default=False,
        help="It requires postgresql server logs seudo-enabled")
    use_py_index = fields.Boolean(
        name="Get cProfiling report", default=False,
        help="Index human-readable cProfile attachment."
        "\nTo access this report, you must open the cprofile attachment view "
        "using debug mode.\nWarning: Uses more resources.")
    date_started = fields.Char(readonly=True)
    date_finished = fields.Char(readonly=True)
    state = fields.Selection([
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
    ], default='disabled', readonly=True, required=True)
    description = fields.Text(readonly=True)
    attachment_count = fields.Integer(compute="_compute_attachment_count")
    pg_log_path = fields.Char(help="Getting the path to the logger",
                              default=_find_loggers_path)
    pg_remote = fields.Char()
    pg_stats_slowest_html = fields.Html(
        "PostgreSQL Stats - Slowest", readonly=True)
    pg_stats_time_consuming_html = fields.Html(
        "PostgreSQL Stats - Time Consuming", readonly=True)
    pg_stats_most_frequent_html = fields.Html(
        "PostgreSQL Stats - Most Frequent", readonly=True)
    py_stats_lines = fields.One2many(
        "profiler.profile.python.line", "profile_id", "PY Stats Lines")

    @api.multi
    def _compute_attachment_count(self):
        for record in self:
            self.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', self._name), ('res_id', '=', record.id)])

    @api.onchange('enable_postgresql')
    def onchange_enable_postgresql(self):
        if not self.enable_postgresql:
            return
        try:
            self.env.cr.execute("SHOW config_file")
        except ProgrammingError:
            pg_config_file = None
        else:
            pg_config_file = self.env.cr.fetchone()[0]
        db_host = tools.config.get('db_host')
        if db_host == 'localhost' or db_host == '127.0.0.1':
            db_host = False
        if db_host and pg_config_file:
            pg_config_file = 'postgres@%s:%s' % (db_host, pg_config_file)
            self.pg_remote = db_host

        self.description = (
            "You need seudo-enable logs from your "
            "postgresql-server configuration file.\n\t- %s\n"
            "or your can looking for the service using: "
            "'ps aux | grep postgres'\n\n"
        ) % pg_config_file
        self.description += """Adds the following parameters:
# Pre-enable logs
logging_collector=on
log_destination='stderr'
log_directory='/var/log/postgresql'
log_filename='postgresql.log'
log_rotation_age=0
log_checkpoints=on
log_hostname=on
log_line_prefix='%t [%p]: [%l-1] db=%d,user=%u '
log_connections=on
log_disconnections=on
lc_messages='C'
log_timezone='UTC'

Reload configuration using the following query:
 - select pg_reload_conf()
Or restart the postgresql server service.

FYI This module will enable the following parameter from the client
    It's not needed added them to configuration file if database user is
     superuser or use PGOPTIONS environment variable in the terminal
     that you start your odoo server.
    If you don't add these parameters or PGOPTIONS this module will try do it.
# Enable logs from postgresql.conf
log_min_duration_statement=0
client_min_messages=notice
log_min_messages=warning
log_min_error_statement=error
log_duration=off
log_error_verbosity=verbose
log_lock_waits=on
log_statement='none'
log_temp_files=0

#  Or enable logs from PGOPTIONS environment variable before to start odoo
#     server
export PGOPTIONS="-c log_min_duration_statement=0 \\
-c client_min_messages=notice -c log_min_messages=warning \\
-c log_min_error_statement=error -c log_connections=on \\
-c log_disconnections=on -c log_duration=off -c log_error_verbosity=verbose \\
-c log_lock_waits=on -c log_statement='none' -c log_temp_files=0"
~/odoo_path/odoo-bin ...
"""

    profile = Profile()
    enabled = None
    pglogs_enabled = None

    # True to activate it False to inactivate None to do nothing
    activate_deactivate_pglogs = None

    # Params dict with values before to change it.
    psql_params_original = {}

    @api.model
    def now_utc(self):
        self.env.cr.execute("SHOW log_timezone")
        zone = self.env.cr.fetchone()[0]
        self.env.cr.execute("SELECT to_char(current_timestamp AT TIME "
                            "ZONE %s, 'YYYY-MM-DD HH24:MI:SS')", (zone,))
        now = self.env.cr.fetchall()[0][0]
        # now = fields.Datetime.to_string(
        #     fields.Datetime.context_timestamp(self, datetime.now()))
        return now

    @api.multi
    def enable(self):
        self.ensure_one()
        if tools.config.get('workers'):
            raise exceptions.UserError(
                _("Start the odoo server using the parameter '--workers=0'"))
        _logger.info("Enabling profiler")
        self.write(dict(
            date_started=self.now_utc(),
            state='enabled'
        ))
        ProfilerProfile.enabled = self.enable_python
        self._reset_postgresql()

    @api.multi
    def _reset_postgresql(self):
        if not self.enable_postgresql:
            return
        if ProfilerProfile.pglogs_enabled:
            _logger.info("Using postgresql.conf or PGOPTIONS predefined.")
            return
        os.environ['PGOPTIONS'] = (
            PGOPTIONS_ENV if self.state == 'enabled' else '')
        self._reset_connection(self.state == 'enabled')

    def _reset_connection(self, enable):
        for connection in sql_db._Pool._connections:
            with connection[0].cursor() as pool_cr:
                params = (PGOPTIONS if enable
                          else ProfilerProfile.psql_params_original)
                for param, value in params.items():
                    try:
                        pool_cr.execute('SET %s TO %s' % (param, value))
                    except (OperationalError, ProgrammingError) as oe:
                        pool_cr.connection.rollback()
                        raise exceptions.UserError(
                            _("It's not possible change parameter.\n%s\n"
                              "Please, disable postgresql or re-enable it "
                              "in order to read the instructions") % str(oe))
            ProfilerProfile.activate_deactivate_pglogs = enable

    def get_stats_string(self, cprofile_path):
        pstats_stream = IO()
        pstats_obj = pstats.Stats(cprofile_path, stream=pstats_stream)
        pstats_obj.sort_stats('cumulative')
        pstats_obj.print_stats()
        pstats_stream.seek(0)
        stats_string = pstats_stream.read()
        pstats_stream = None
        return stats_string

    @api.multi
    def dump_postgresql_logs(self, indexed=None):
        self.ensure_one()
        self.description = ''
        pgbadger_cmd = self._get_pgbadger_command()
        if pgbadger_cmd is None:
            return
        pgbadger_cmd_str = subprocess.list2cmdline(pgbadger_cmd)
        self.description += (
            '\nRunning the command: %s') % pgbadger_cmd_str
        result = tools.exec_command_pipe(*pgbadger_cmd)
        datas = result[1].read()
        if not datas:
            self.description += "\nPgbadger output is empty!"
            return
        fname = self._get_attachment_name("pg_stats", ".html")
        self.env['ir.attachment'].create({
            'name': fname,
            'res_id': self.id,
            'res_model': self._name,
            'datas': base64.b64encode(datas),
            'datas_fname': fname,
            'description': 'pgbadger html output',
        })
        xpaths = [
            '//*[@id="slowest-individual-queries"]',
            '//*[@id="time-consuming-queries"]',
            '//*[@id="most-frequent-queries"]',
        ]
        # pylint: disable=unbalanced-tuple-unpacking
        self.pg_stats_slowest_html, self.pg_stats_time_consuming_html, \
            self.pg_stats_most_frequent_html = self._compute_pgbadger_html(
                datas, xpaths)

    @staticmethod
    def _compute_pgbadger_html(html_doc, xpaths):
        html = lxml.html.document_fromstring(html_doc)
        result = []
        for this_xpath in xpaths:
            this_result = html.xpath(this_xpath)
            result.append(
                tools.html_sanitize(lxml.html.tostring(this_result[0])))
        return result

    @api.multi
    def _get_pgbadger_command(self):
        self.ensure_one()
        # TODO: Catch early the following errors.
        try:
            pgbadger_bin = tools.find_in_path('pgbadger')
        except IOError:
            self.description += (
                "\nInstall 'apt-get install pgbadger'")
            return
        try:
            if not self.pg_log_path:
                raise IOError
            with open(self.pg_log_path, "r"):
                pass
        except IOError:
            self.description += (
                "\nCheck if exists and has permission to read the log file."
                "\nMaybe running: chmod 604 '%s'"
            ) % self.pg_log_path
            return
        pgbadger_cmd = [
            pgbadger_bin, '-f', 'stderr', '--sample', '15',
            '-o', '-', '-x', 'html', '--quiet',
            '-T', self.name,
            '-d', self.env.cr.dbname,
            '-b', self.date_started,
            '-e', self.date_finished,
            self.pg_log_path,
        ]
        return pgbadger_cmd

    def _get_attachment_name(self, prefix, suffix):
        started = fields.Datetime.from_string(
            self.date_started).strftime(DATETIME_FORMAT_FILE)
        finished = fields.Datetime.from_string(
            self.date_finished).strftime(DATETIME_FORMAT_FILE)
        fname = '%s_%d_%s_to_%s%s' % (
            prefix, self.id, started, finished, suffix)
        return fname

    @api.model
    def dump_stats(self):
        attachment = None
        with tools.osutil.tempdir() as dump_dir:
            cprofile_fname = self._get_attachment_name("py_stats", ".cprofile")
            cprofile_path = os.path.join(dump_dir, cprofile_fname)
            _logger.info("Dumping cProfile '%s'", cprofile_path)
            ProfilerProfile.profile.dump_stats(cprofile_path)
            with open(cprofile_path, "rb") as f_cprofile:
                datas = f_cprofile.read()
            if datas and datas != CPROFILE_EMPTY_CHARS:
                attachment = self.env['ir.attachment'].create({
                    'name': cprofile_fname,
                    'res_id': self.id,
                    'res_model': self._name,
                    'datas': base64.b64encode(datas),
                    'datas_fname': cprofile_fname,
                    'description': 'cProfile dump stats',
                })
                _logger.info("A datas was saved, here %s", attachment.name)
                try:
                    if self.use_py_index:
                        py_stats = self.get_stats_string(cprofile_path)
                        self.env['profiler.profile.python.line'].search([
                            ('profile_id', '=', self.id)]).unlink()
                        for py_stat_line in py_stats.splitlines():
                            py_stat_line = py_stat_line.strip('\r\n ')
                            py_stat_line_match = LINE_STATS_RE.match(
                                py_stat_line) if py_stat_line else None
                            if not py_stat_line_match:
                                continue
                            data = dict((
                                field, py_stat_line_match.group(field))
                                for field in PY_STATS_FIELDS)
                            data['rcalls'], data['calls'] = (
                                "%(ncalls)s/%(ncalls)s" % data).split('/')[:2]
                            self.env['profiler.profile.python.line'].create({
                                'cprof_tottime': data['tottime'],
                                'cprof_ncalls': data['calls'],
                                'cprof_nrcalls': data['rcalls'],
                                'cprof_ttpercall': data['tt_percall'],
                                'cprof_cumtime': data['cumtime'],
                                'cprof_ctpercall': data['ct_percall'],
                                'cprof_fname': (
                                    "%(file)s:%(lineno)s (%(method)s)" % data),
                                'profile_id': self.id,
                            })
                        attachment.index_content = py_stats
                except IOError:
                    # Fancy feature but not stop process if fails
                    _logger.info("There was an error while getting the stats"
                                 "from the cprofile_path")
                    # pylint: disable=unnecessary-pass
                    pass
                self.dump_postgresql_logs()
                _logger.info("cProfile stats stored.")
            else:
                _logger.info("cProfile stats empty.")
        return attachment

    @api.multi
    def clear(self, reset_date=True):
        self.ensure_one()
        _logger.info("Clear profiler")
        if reset_date:
            self.date_started = self.now_utc()
        ProfilerProfile.profile.clear()

    @api.multi
    def disable(self):
        self.ensure_one()
        _logger.info("Disabling profiler")
        ProfilerProfile.enabled = False
        self.state = 'disabled'
        self.date_finished = self.now_utc()
        self.dump_stats()
        self.clear(reset_date=False)
        self._reset_postgresql()

    @staticmethod
    @contextmanager
    def profiling():
        """Thread local profile management, according to the shared "enabled"
        """
        if ProfilerProfile.enabled:
            _logger.debug("Catching profiling")
            ProfilerProfile.profile.enable()
        try:
            yield
        finally:
            if ProfilerProfile.enabled:
                ProfilerProfile.profile.disable()

    @api.multi
    def action_view_attachment(self):
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', self._name), ('res_id', '=', self.id)])
        action = self.env.ref("base.action_attachment").read()[0]
        action['domain'] = [('id', 'in', attachments.ids)]
        return action

    @api.model
    def set_pgoptions_enabled(self):
        """Verify if postgresql has configured the parameters for logging"""
        ProfilerProfile.pglogs_enabled = True
        pgoptions_enabled = bool(os.environ.get('PGOPTIONS'))
        _logger.info('Logging enabled from environment '
                     'variable PGOPTIONS? %s', pgoptions_enabled)
        if pgoptions_enabled:
            return
        pgparams_required = {
            'log_min_duration_statement': '0',
        }
        for param, value in pgparams_required.items():
            # pylint: disable=sql-injection
            self.env.cr.execute("SHOW %s" % param)
            db_value = self.env.cr.fetchone()[0].lower()
            if value.lower() != db_value:
                ProfilerProfile.pglogs_enabled = False
                break
        ProfilerProfile.psql_params_original = self.get_psql_params(
            self.env.cr, PGOPTIONS.keys())
        _logger.info('Logging enabled from postgresql.conf? %s',
                     ProfilerProfile.pglogs_enabled)

    @staticmethod
    def get_psql_params(cr, params):
        result = {}
        for param in set(params):
            # pylint: disable=sql-injection
            cr.execute('SHOW %s' % param)
            result.update(cr.dictfetchone())
        return result

    @api.model
    def _setup_complete(self):
        self.set_pgoptions_enabled()
        return super(ProfilerProfile, self)._setup_complete()
