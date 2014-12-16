# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import logging
import platform
import os
import sys
from raven import Client
try:
    from bzrlib.branch import Branch as Bzr
    from bzrlib.errors import NotBranchError
except ImportError:
    Bzr = False
try:
    from git import Git, GitCommandError
except ImportError:
    Git = False

from openerp.tools import config
_logger = logging.getLogger(__name__)


class OdooClient(Client):
    """Subclass raven.Client to be able to report Module versions and
     commit numbers"""

    def __init__(self, dsn=None, **options):
        """Set up Sentry Client, add version numbers to sentry package
        Send a message when Activate
        """
        # Send the following library versions and include all eggs in sys.path
        include_paths = [
            'openerp',
            'sentry',
            'raven',
            'raven_sanitize_openerp',
        ] + [os.path.basename(i).split('-')[0]
             for i in sys.path if i.endswith('.egg')]
        # Add tags, OS and bzr revisions for Server and Addons
        tags = {
            'OS': (" ".join(platform.linux_distribution()).strip() or
                   " ".join(platform.win32_ver()).strip() or
                   " ".join((platform.system(), platform.release(),
                             platform.machine()))),
        }
        self.revnos = {}
        super(OdooClient, self).__init__(
            dsn=dsn, include_paths=include_paths, tags=tags, **options)
        self.set_rev_versions()
        # Create and test message for Sentry
        self.captureMessage(u'Sentry Tracking Activated!')

    def set_rev_versions(self):
        """Given path, get source and revno, careful not to raise any
        exceptions"""
        paths = set(config.get('addons_path').split(','))
        bzr_paths = (
            p for p in paths if os.path.exists(os.path.join(p, '.bzr'))
        )
        git_paths = (
            p for p in paths if os.path.exists(os.path.join(p, '.git'))
        )
        if Bzr:
            self.set_rev_bzr_version(bzr_paths)
        if Git:
            self.set_rev_git_version(git_paths)

    def set_rev_bzr_version(self, paths):
        for path in paths:
            try:
                branch, rel_path = Bzr.open_containing(path)
                branch.lock_read()
                # Clean name
                name = branch.get_parent()
                name = name.replace(u'bazaar.launchpad.net/', u'lp:')
                name = name.replace(u'%7E', u'~')
                name = name.replace(u'%2Bbranch/', u'')
                name = name.replace(u'bzr+ssh://', u'')
                self.revnos[name] = u'r%i' % branch.revno()
                branch.unlock()
            except NotBranchError:
                continue
            finally:
                if branch.is_locked():
                    branch.unlock()

    def set_rev_git_version(self, paths):
        for path in paths:
            try:
                git_repo = Git(path)
                name = os.path.basename(path)
                self.revnos[name] = git_repo.log('-1', pretty='%H')
            except GitCommandError:
                continue

    def build_msg(self, event_type, data=None, date=None,
                  time_spent=None, extra=None, stack=None, public_key=None,
                  tags=None, **kwargs):
        """Add revnos to msg's modules"""
        res = super(OdooClient, self).build_msg(
            event_type, data, date, time_spent, extra, stack, public_key,
            tags, **kwargs)
        res['modules'] = dict(res['modules'].items() + self.revnos.items())
        # Sanitize frames from dispatch since they contain passwords
        try:
            for values in res['exception']['values']:
                values['stacktrace']['frames'] = [
                    f for f in values['stacktrace']['frames']
                    if f.get('function') not in ['dispatch', 'dispatch_rpc']
                ]
        except KeyError:
            pass
        return res
