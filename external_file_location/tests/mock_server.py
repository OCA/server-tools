# coding: utf-8
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
# @ 2015 Valentin CHEMIERE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
