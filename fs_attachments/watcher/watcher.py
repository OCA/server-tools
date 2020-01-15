# Copyright (c) 2015-2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2016 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

import logging
import os
from threading import Thread
import time
import odoo
import inotify.adapters
from watchdog.observers import Observer
from watchdog.observers.api import DEFAULT_OBSERVER_TIMEOUT
from watchdog.events import FileSystemEventHandler
from odoo.service import server
from odoo.tools import config
import psycopg2
from pathlib import Path
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from contextlib import closing, contextmanager
try:
    from odoo.addons.server_environment import serv_config
    if serv_config.has_section('queue_job'):
        queue_job_config = serv_config['queue_job']
    else:
        queue_job_config = {}
except ImportError:
    queue_job_config = config.misc.get('queue_job', {})


_logger = logging.getLogger(__name__)

START_DELAY = 5
ERROR_RECOVERY_DELAY = 5


# Here we monkey patch the Odoo server to start the job runner thread
# in the main server process (and not in forked workers). This is
# very easy to deploy as we don't need another startup script.
class Database(object):

    def __init__(self, db_name):
        self.db_name = db_name
        db_or_uri, connection_info = odoo.sql_db.connection_info_for(db_name)
        self.conn = psycopg2.connect(**connection_info)
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    def close(self):
        # pylint: disable=except-pass
        # if close fail for any reason, it's either because it's already closed
        # and we don't care, or for any reason but anyway it will be closed on
        # del
        try:
            self.conn.close()
        except Exception:
            pass
        self.conn = None

    def get_watcher_directories(self):
        directories = {}
        with closing(self.conn.cursor()) as cr:
            cr.execute("SELECT id, filesystem_storage_path FROM res_company WHERE not filesystem_storage_path is null")
            for row in cr.fetchall():
                directories[row[1]] = {
                    'company_id': row[0]
                }
        return directories

    def has_filesystem_storage(self):
        with closing(self.conn.cursor()) as cr:
            cr.execute(
                "SELECT 1 FROM ir_module_module WHERE name=%s AND state=%s",
                ('fs_attachments', 'installed')
            )
            return cr.fetchone()


class FSEventHandler(FileSystemEventHandler):
    def __init__(self, watcherThread):
        self.watcherThread = watcherThread
        self.directories = None
        super(FSEventHandler, self).__init__()

    def build_directories(self):
        self.directories = {}
        for dbname in self.watcherThread.db_by_name:
            dbstruct = self.watcherThread.db_by_name[dbname]
            for dir in dbstruct['directories']:
                self.directories[dir] = dbstruct['directories'][dir]

    def sync_in_environment(self, operation, filepath):
        if not self.directories:
            self.build_directories()
        path = Path(filepath)
        while(str(path) not in self.directories):
            path = path.parent
            if str(path) == path.root:
                break
        if str(path) in self.directories:
            directory = self.directories[str(path)]
            rel_file_path = os.path.relpath(filepath, str(path))
            with odoo.api.Environment.manage():
                cr = self.watcherThread.db_by_name[directory['dbname']]['registry'].cursor()
                try:
                    env = odoo.api.Environment(cr, 1, {})
                    if operation == 'delete':
                        env['ir.attachment'].filesystem_delete_event(directory['company_id'], rel_file_path)
                    elif operation == 'create':
                        env['ir.attachment'].filesystem_create_event(directory['company_id'], rel_file_path, filepath)
                    cr.commit()
                except:
                    cr.rollback()
                finally:
                    cr.close()
            _logger.info("Got DBName %s", directory['dbname'])

    def on_created(self, event):
        self.sync_in_environment("create", event.src_path)
        _logger.info(f"{event.src_path} has been created!")

    def on_deleted(self, event):
        self.sync_in_environment("delete", event.src_path)
        _logger.info(f"Someone deleted {event.src_path}!")

    def on_modified(self, event):
        _logger.info(f"{event.src_path} has been modified")

    def on_moved(self, event):
        self.sync_in_environment("delete", event.src_path)
        self.sync_in_environment("create", event.dest_path)
        _logger.info(f"Someone moved {event.src_path} to {event.dest_path}")


class WatcherThread(Observer):

    def __init__(self, timeout=DEFAULT_OBSERVER_TIMEOUT):
        super(WatcherThread, self).__init__(timeout)
        self.db_by_name = {}

    def get_db_names(self):
        if config['db_name']:
            db_names = config['db_name'].split(',')
        else:
            db_names = odoo.service.db.exp_list(True)
        return db_names

    def initialize_databases(self):
        for db_name in self.get_db_names():
            db = Database(db_name)
            if not db.has_filesystem_storage:
                _logger.debug('filesystem storage is not installed for db %s', db_name)
            else:
                # Add Observer for every company
                directories = db.get_watcher_directories()
                for dir in directories:
                    self.schedule(self.event_handler, dir, recursive=True)
                    directories[dir]['dbname'] = db_name
                registry = odoo.modules.registry.Registry.new(db_name)
                self.db_by_name[db_name] = {
                    'db': db,
                    'directories': directories,
                    'dbname': db_name,
                    'registry': registry
                }
                _logger.info('filesystem watcher ready for db %s', db_name)

    def close_databases(self):
        for dbname in self.db_by_name.items():
            dbstruct = self.db_by_name[dbname]
            db = dbstruct['db']
            try:
                db.close()
            except Exception:
                _logger.warning('error closing database %s',
                                dbstruct['db_name'], exc_info=True)
        self.db_by_name = {}

    def start(self):
        # sleep a bit to let the workers start at ease
        time.sleep(START_DELAY)
        # Create Eventhandler object
        self.event_handler = FSEventHandler(self)
        # Initialize the databases
        self.initialize_databases()
        super(WatcherThread, self).start()

    def stop(self):
        self.close_databases()


runner_thread = None


def _is_runner_enabled():
    return True


def _start_watch_thread(server_type):
    global runner_thread
    if not config['stop_after_init']:
        _logger.info("starting watcher thread (in %s)",
                     server_type)
        runner_thread = WatcherThread()
        runner_thread.start()


orig_prefork_start = server.PreforkServer.start
orig_prefork_stop = server.PreforkServer.stop
orig_threaded_start = server.ThreadedServer.start
orig_threaded_stop = server.ThreadedServer.stop


def prefork_start(server, *args, **kwargs):
    res = orig_prefork_start(server, *args, **kwargs)
    _start_watch_thread("prefork server")
    return res


def prefork_stop(server, graceful=True):
    global runner_thread
    if runner_thread:
        runner_thread.stop()
    res = orig_prefork_stop(server, graceful)
    if runner_thread:
        runner_thread.join()
        runner_thread = None
    return res


def threaded_start(server, *args, **kwargs):
    res = orig_threaded_start(server, *args, **kwargs)
    _start_watch_thread("threaded server")
    return res


def threaded_stop(server):
    global runner_thread
    if runner_thread:
        runner_thread.stop()
    res = orig_threaded_stop(server)
    if runner_thread:
        runner_thread.join()
        runner_thread = None
    return res


server.PreforkServer.start = prefork_start
server.PreforkServer.stop = prefork_stop
server.ThreadedServer.start = threaded_start
server.ThreadedServer.stop = threaded_stop