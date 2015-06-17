# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import mock
from contextlib import contextmanager
from collections import defaultdict


class MultiResponse(dict):
    pass


class ConnMock(object):

    def __init__(self, response):
        self.response = response
        self._calls = []
        self.call_count = defaultdict(int)

    def __getattribute__(self, method):
        if method not in ('_calls', 'response', 'call_count'):
            def callable(*args, **kwargs):
                self._calls.append({
                    'method': method,
                    'args': args,
                    'kwargs': kwargs,
                })
                call = self.response[method]
                if isinstance(call, MultiResponse):
                    call = call[self.call_count[method]]
                    self.call_count[method] += 1
                return call

            return callable
        else:
            return super(ConnMock, self).__getattribute__(method)

    def __call__(self, *args, **kwargs):
        return self

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def __repr__(self, *args, **kwargs):
        return self

    def __getitem__(self, key):
        return


@contextmanager
def server_mock(response):
    with mock.patch('fs.sftpfs.SFTPFS', ConnMock(response)) as SFTPFS:
        yield SFTPFS._calls
