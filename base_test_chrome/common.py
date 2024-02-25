# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# nearly verbatim copy of odoo12/tests/common.py
# flake8: noqa
import base64
import inspect
import json
import logging
import os
import platform
import requests
import shutil
import signal
import subprocess
import tempfile
import threading
import time
import unittest
import werkzeug.urls
import xmlrpclib
from datetime import datetime
from openerp.tests.common import TransactionCase

try:
    import websocket
except ImportError:
    # chrome headless tests will be skipped
    websocket = None

import openerp
from openerp import api
from openerp.tools.misc import find_in_path
from openerp.tests.common import HOST, PORT


def get_db_name():
    db = openerp.tools.config['db_name']
    # If the database name is not provided on the command-line,
    # use the one on the thread (which means if it is provided on
    # the command-line, this will break when installing another
    # database from XML-RPC).
    if not db and hasattr(threading.current_thread(), 'dbname'):
        return threading.current_thread().dbname
    return db


class ChromeBrowser():
    """ Helper object to control a Chrome headless process. """

    def __init__(self, logger):
        self._logger = logger
        if websocket is None:
            self._logger.warning("websocket-client module is not installed")
            raise unittest.SkipTest("websocket-client module is not installed")
        self.devtools_port = PORT + 2
        self.ws_url = ''  # WebSocketUrl
        self.ws = None  # websocket
        self.request_id = 0
        self.user_data_dir = tempfile.mkdtemp(suffix='_chrome_odoo')
        self.chrome_process = None
        self.screencast_frames = []
        self._chrome_start()
        self._find_websocket()
        self._logger.info('Websocket url found: %s', self.ws_url)
        self._open_websocket()
        self._logger.info('Enable chrome headless console log notification')
        self._websocket_send('Runtime.enable')
        self._logger.info('Chrome headless enable page notifications')
        self._websocket_send('Page.enable')
        self.sigxcpu_handler = None
        if os.name == 'posix':
            self.sigxcpu_handler = signal.getsignal(signal.SIGXCPU)
            signal.signal(signal.SIGXCPU, self.signal_handler)

    def signal_handler(self, sig, frame):
        if sig == signal.SIGXCPU:
            self._logger.info(
                'CPU time limit reached, stopping Chrome and shutting down'
            )
            self.stop()
            os._exit(0)

    def stop(self):
        if self.chrome_process is not None:
            self._logger.info("Closing chrome headless with pid %s", self.chrome_process.pid)
            self._websocket_send('Browser.close')
            if self.chrome_process.poll() is None:
                self._logger.info("Terminating chrome headless with pid %s", self.chrome_process.pid)
                self.chrome_process.terminate()
                self.chrome_process.wait()
        if self.user_data_dir and os.path.isdir(self.user_data_dir) and self.user_data_dir != '/':
            self._logger.info('Removing chrome user profile "%s"', self.user_data_dir)
            shutil.rmtree(self.user_data_dir, ignore_errors=True)
        # Restore previous signal handler
        if self.sigxcpu_handler and os.name == 'posix':
            signal.signal(signal.SIGXCPU, self.sigxcpu_handler)

    @property
    def executable(self):
        system = platform.system()
        if system == 'Linux':
            for bin_ in ['google-chrome', 'chromium', 'chromium-browser']:
                if find_in_path(bin_):
                    return find_in_path(bin_)

        elif system == 'Darwin':
            bins = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/Applications/Chromium.app/Contents/MacOS/Chromium',
            ]
            for bin_ in bins:
                if os.path.exists(bin_):
                    return bin_

        elif system == 'Windows':
            # TODO: handle windows platform: https://stackoverflow.com/a/40674915
            pass

        raise unittest.SkipTest("Chrome executable not found")

    def _chrome_start(self):
        if self.chrome_process is not None:
            return
        switches = {
            '--headless': '',
            '--disable-gpu': '',
            '--enable-logging': 'stderr',
            '--no-default-browser-check': '',
            '--no-first-run': '',
            '--disable-extensions': '',
            '--user-data-dir': self.user_data_dir,
            '--disable-translate': '',
            '--window-size': '1366x768',
            '--remote-debugging-address': HOST,
            '--remote-debugging-port': str(self.devtools_port),
            '--no-sandbox': '',
        }
        cmd = [self.executable]
        cmd += ['%s=%s' % (k, v) if v else k for k, v in switches.items()]
        url = 'about:blank'
        cmd.append(url)
        self._logger.info('chrome_run executing %s', ' '.join(cmd))
        try:
            self.chrome_process = subprocess.Popen(
                cmd,
                stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'),
            )
        except OSError:
            raise unittest.SkipTest("%s not found" % cmd[0])
        self._logger.info('Chrome pid: %s', self.chrome_process.pid)

    def _find_websocket(self):
        version = self._json_command('version')
        self._logger.info('Browser version: %s', version['Browser'])
        try:
            infos = self._json_command('')[0]  # Infos about the first tab
        except IndexError:
            self._logger.warning('No tab found in Chrome')
            self.stop()
            raise unittest.SkipTest('No tab found in Chrome')
        self.ws_url = infos['webSocketDebuggerUrl']
        self._logger.info('Chrome headless temporary user profile dir: %s', self.user_data_dir)

    def _json_command(self, command, timeout=3):
        """
        Inspect dev tools with get
        Available commands:
            '' : return list of tabs with their id
            list (or json/): list tabs
            new : open a new tab
            activate/ + an id: activate a tab
            close/ + and id: close a tab
            version : get chrome and dev tools version
            protocol : get the full protocol
        """
        self._logger.info("Issuing json command %s", command)
        command = os.path.join('json', command).strip('/')
        while timeout > 0:
            try:
                url = werkzeug.urls.url_join('http://%s:%s/' % (HOST, self.devtools_port), command)
                self._logger.info('Url : %s', url)
                r = requests.get(url, timeout=3)
                if r.ok:
                    return r.json()
                return {'status_code': r.status_code}
            except requests.ConnectionError:
                time.sleep(0.1)
                timeout -= 0.1
            except requests.exceptions.ReadTimeout:
                break
        self._logger.error('Could not connect to chrome debugger')
        raise unittest.SkipTest("Cannot connect to chrome headless")

    def _open_websocket(self):
        self.ws = websocket.create_connection(self.ws_url)
        if self.ws.getstatus() != 101:
            raise unittest.SkipTest("Cannot connect to chrome dev tools")
        self.ws.settimeout(0.01)

    def _websocket_send(self, method, params=None):
        """
        send chrome devtools protocol commands through websocket
        """
        sent_id = self.request_id
        payload = {
            'method': method,
            'id':  sent_id,
        }
        if params:
            payload.update({'params': params})
        self.ws.send(json.dumps(payload))
        self.request_id += 1
        return sent_id

    def _websocket_wait_id(self, awaited_id, timeout=10):
        """
        blocking wait for a certain id in a response
        warning other messages are discarded
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                res = json.loads(self.ws.recv())
            except websocket.WebSocketTimeoutException:
                res = None
            if res and res.get('id') == awaited_id:
                return res
        self._logger.info('timeout exceeded while waiting for id : %d', awaited_id)
        return {}

    def _websocket_wait_event(self, method, params=None, timeout=10):
        """
        blocking wait for a particular event method and eventually a dict of params
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                res = json.loads(self.ws.recv())
            except websocket.WebSocketTimeoutException:
                res = None
            if res and res.get('method', '') == method:
                if params:
                    if set(params).issubset(set(res.get('params', {}))):
                        return res
                else:
                    return res
            elif res:
                self._logger.debug('chrome devtools protocol event: %s', res)
        self._logger.info('timeout exceeded while waiting for : %s', method)

    def _get_shotname(self, prefix, ext):
        """ return a unique filename for screenshot or screencast"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        base_file = os.path.splitext(openerp.tools.config['logfile'])[0]
        name = '%s_%s_%s.%s' % (base_file, prefix, timestamp, ext)
        return name

    def take_screenshot(self, prefix='failed'):
        if not openerp.tools.config['logfile']:
            self._logger.info('Screenshot disabled !')
            return None
        ss_id = self._websocket_send('Page.captureScreenshot')
        self._logger.info('Asked for screenshot (id: %s)', ss_id)
        res = self._websocket_wait_id(ss_id)
        base_png = res.get('result', {}).get('data')
        decoded = base64.b64decode(base_png)
        outfile = self._get_shotname(prefix, 'png')
        with open(outfile, 'wb') as f:
            f.write(decoded)
        self._logger.info('Screenshot in: %s', outfile)

    def _save_screencast(self, prefix='failed'):
        # could be encododed with something like that
        #  ffmpeg -framerate 3 -i frame_%05d.png  output.mp4
        if not openerp.tools.config['logfile']:
            self._logger.info('Screencast disabled !')
            return None
        sdir = tempfile.mkdtemp(suffix='_chrome_odoo_screencast')
        nb = 0
        for frame in self.screencast_frames:
            outfile = os.path.join(sdir, 'frame_%05d.png' % nb)
            with open(outfile, 'wb') as f:
                f.write(base64.b64decode(frame.get('data')))
                nb += 1
        framerate = int(nb / (self.screencast_frames[nb-1].get('metadata').get('timestamp') - self.screencast_frames[0].get('metadata').get('timestamp')))
        outfile = self._get_shotname(prefix, 'mp4')
        r = subprocess.call(['ffmpeg', '-framerate', str(framerate), '-i', '%s/frame_%%05d.png' % sdir, outfile])
        shutil.rmtree(sdir)
        if r == 0:
            self._logger.info('Screencast in: %s', outfile)

    def start_screencast(self):
        self._websocket_send('Page.startScreencast', {'params': {'everyNthFrame': 5, 'maxWidth': 683, 'maxHeight': 384}})

    def set_cookie(self, name, value, path, domain):
        params = {'name': name, 'value': value, 'path': path, 'domain': domain}
        _id = self._websocket_send('Network.setCookie', params=params)
        return self._websocket_wait_id(_id)

    def _wait_ready(self, ready_code, timeout=60):
        self._logger.info('Evaluate ready code "%s"', ready_code)
        awaited_result = {'result': {'type': 'boolean', 'value': True}}
        ready_id = self._websocket_send('Runtime.evaluate', params={'expression': ready_code})
        last_bad_res = ''
        start_time = time.time()
        tdiff = time.time() - start_time
        has_exceeded = False
        while tdiff < timeout:
            try:
                res = json.loads(self.ws.recv())
            except websocket.WebSocketTimeoutException:
                res = None
            if res and res.get('id') == ready_id:
                if res.get('result') == awaited_result:
                    return True
                else:
                    last_bad_res = res
                    ready_id = self._websocket_send('Runtime.evaluate', params={'expression': ready_code})
            tdiff = time.time() - start_time
            if tdiff >= 2 and not has_exceeded:
                has_exceeded = True
                self._logger.warning('The ready code takes too much time : %s', tdiff)

        self.take_screenshot(prefix='failed_ready')
        self._logger.info('Ready code last try result: %s', last_bad_res or res)
        return False

    def _wait_code_ok(self, code, timeout):
        self._logger.info('Evaluate test code "%s"', code)
        code_id = self._websocket_send('Runtime.evaluate', params={'expression': code})
        start_time = time.time()
        logged_error = False
        while time.time() - start_time < timeout:
            try:
                res = json.loads(self.ws.recv())
            except websocket.WebSocketTimeoutException:
                res = None
            if res and res.get('id', -1) == code_id:
                self._logger.info('Code start result: %s', res)
                if res.get('result', {}).get('result').get('subtype', '') == 'error':
                    self._logger.error("Running code returned an error")
                    return False
            elif res and res.get('method') == 'Runtime.consoleAPICalled' and res.get('params', {}).get('type') in ('log', 'error'):
                logs = res.get('params', {}).get('args')
                log_type = res.get('params', {}).get('type')
                content = " ".join([unicode(log.get('value', '')) for log in logs])
                if log_type == 'error':
                    self._logger.error(content)
                    logged_error = True
                else:
                    self._logger.info('console log: %s', content)
                for log in logs:
                    if log.get('type', '') == 'string' and log.get('value', '').lower() == 'ok':
                        # it is possible that some tests returns ok while an error was shown in logs.
                        # since runbot should always be red in this case, better explicitly fail.
                        if logged_error:
                            return False
                        return True
                    elif log.get('type', '') == 'string' and log.get('value', '').lower().startswith('error'):
                        self.take_screenshot()
                        self._save_screencast()
                        return False
            elif res and res.get('method') == 'Page.screencastFrame':
                self.screencast_frames.append(res.get('params'))
            elif res:
                self._logger.debug('chrome devtools protocol event: %s', res)
        self._logger.error('Script timeout exceeded : %s', (time.time() - start_time))
        self.take_screenshot()
        return False

    def navigate_to(self, url, wait_stop=False):
        self._logger.info('Navigating to: "%s"', url)
        nav_id = self._websocket_send('Page.navigate', params={'url': url})
        nav_result = self._websocket_wait_id(nav_id)
        self._logger.info("Navigation result: %s", nav_result)
        frame_id = nav_result.get('result', {}).get('frameId', '')
        if wait_stop and frame_id:
            self._logger.info('Waiting for frame "%s" to stop loading', frame_id)
            self._websocket_wait_event('Page.frameStoppedLoading', params={'frameId': frame_id})

    def clear(self):
        self._websocket_send('Page.stopScreencast')
        self.screencast_frames = []
        self._websocket_send('Page.stopLoading')
        self._logger.info('Deleting cookies and clearing local storage')
        dc_id = self._websocket_send('Network.clearBrowserCookies')
        self._websocket_wait_id(dc_id)
        cl_id = self._websocket_send('Runtime.evaluate', params={'expression': 'localStorage.clear()'})
        self._websocket_wait_id(cl_id)
        self.navigate_to('about:blank', wait_stop=True)


class HttpCase(TransactionCase):
    """ Transactional HTTP TestCase with url_open and Chrome headless helpers.
    """
    registry_test_mode = True
    browser = None

    def __init__(self, methodName='runTest'):
        super(HttpCase, self).__init__(methodName)
        # v8 api with correct xmlrpc exception handling.
        self.xmlrpc_url = url_8 = 'http://%s:%d/xmlrpc/2/' % (HOST, PORT)
        self.xmlrpc_common = xmlrpclib.ServerProxy(url_8 + 'common')
        self.xmlrpc_db = xmlrpclib.ServerProxy(url_8 + 'db')
        self.xmlrpc_object = xmlrpclib.ServerProxy(url_8 + 'object')
        cls = type(self)
        self._logger = logging.getLogger('%s.%s' % (cls.__module__, cls.__name__))

    @classmethod
    def start_browser(cls, logger):
        # start browser on demand
        if cls.browser is None:
            cls.browser = ChromeBrowser(logger)

    @classmethod
    def tearDownClass(cls):
        if cls.browser:
            cls.browser.stop()
            cls.browser = None
        super(HttpCase, cls).tearDownClass()

    def setUp(self):
        super(HttpCase, self).setUp()

        if self.registry_test_mode:
            self.registry.enter_test_mode()
            self.addCleanup(self.registry.leave_test_mode)
        # setup a magic session_id that will be rollbacked
        self.session = openerp.http.root.session_store.new()
        self.session_id = self.session.sid
        self.session.db = get_db_name()
        openerp.http.root.session_store.save(self.session)
        # setup an url opener helper
        self.opener = requests.Session()
        self.opener.cookies['session_id'] = self.session_id

    def url_open(self, url, data=None, timeout=10):
        if url.startswith('/'):
            url = "http://%s:%s%s" % (HOST, PORT, url)
        if data:
            return self.opener.post(url, data=data, timeout=timeout)
        return self.opener.get(url, timeout=timeout)

    def _wait_remaining_requests(self):
        t0 = int(time.time())
        for thread in threading.enumerate():
            if thread.name.startswith('openerp.service.http.request.'):
                join_retry_count = 10
                while thread.isAlive():
                    # Need a busyloop here as thread.join() masks signals
                    # and would prevent the forced shutdown.
                    thread.join(0.05)
                    join_retry_count -= 1
                    if join_retry_count < 0:
                        self._logger.warning("Stop waiting for thread %s handling request for url %s",
                                        thread.name, getattr(thread, 'url', '<UNKNOWN>'))
                        break
                    time.sleep(0.5)
                    t1 = int(time.time())
                    if t0 != t1:
                        self._logger.info('remaining requests')
                        openerp.tools.misc.dumpstacks()
                        t0 = t1

    def authenticate(self, user, password):
        # stay non-authenticated
        if user is None:
            return

        db = get_db_name()
        uid = self.registry['res.users'].authenticate(db, user, password, None)
        env = api.Environment(self.cr, uid, {})

        # self.session.authenticate(db, user, password, uid=uid)
        # OpenERPSession.authenticate accesses the current request, which we
        # don't have, so reimplement it manually...
        session = self.session

        session.db = db
        session.uid = uid
        session.login = user
        session.password = password
        session.context = env['res.users'].context_get() or {}
        session.context['uid'] = uid
        session._fix_lang(session.context)

        openerp.http.root.session_store.save(session)
        if self.browser:
            self._logger.info('Setting session cookie in browser')
            self.browser.set_cookie('session_id', self.session_id, '/', HOST)

    def browser_js(self, url_path, code, ready='', login=None, timeout=60, **kw):
        """ Test js code running in the browser
        - optionnally log as 'login'
        - load page given by url_path
        - wait for ready object to be available
        - eval(code) inside the page

        To signal success test do:
        console.log('ok')

        To signal failure do:
        console.log('error')

        If neither are done before timeout test fails.
        """
        # increase timeout if coverage is running
        if any(
                s[1].endswith('/coverage/execfile.py')
                for s in inspect.stack()
                if s[1]
        ):
            timeout = timeout * 1.5
        self.start_browser(self._logger)

        try:
            self.authenticate(login, login)
            base_url = "http://%s:%s" % (HOST, PORT)
            ICP = self.env['ir.config_parameter']
            ICP.set_param('web.base.url', base_url)
            url = "%s%s" % (base_url, url_path or '/')
            self._logger.info('Open "%s" in browser', url)

            if openerp.tools.config['logfile']:
                self._logger.info('Starting screen cast')
                self.browser.start_screencast()
            self.browser.navigate_to(url, wait_stop=not bool(ready))

            # Needed because tests like test01.js (qunit tests) are passing a ready
            # code = ""
            ready = ready or "document.readyState === 'complete'"
            self.assertTrue(self.browser._wait_ready(ready), 'The ready "%s" code was always falsy' % ready)
            if code:
                message = 'The test code "%s" failed' % code
            else:
                message = "Some js test failed"
            self.assertTrue(self.browser._wait_code_ok(code, timeout), message)
        finally:
            # clear browser to make it stop sending requests, in case we call
            # the method several times in a test method
            self.browser.clear()
            self._wait_remaining_requests()

    phantom_js = browser_js
