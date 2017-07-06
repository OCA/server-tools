# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from werkzeug import exceptions

from odoo import _


class OauthApiException(exceptions.BadRequest):
    pass


class OauthInvalidTokenException(exceptions.Unauthorized):

    def __init__(self):
        super(OauthInvalidTokenException, self).__init__(
            _('Invalid or expired token'),
        )
        self.traceback = ('', '', '')


class OauthScopeValidationException(exceptions.Forbidden):

    def __init__(self, code='unknown'):
        msg = _(
            'There was an error validating the attempted action against '
            'your session\'s authorized scope. The error code is: %s',
        )
        super(OauthScopeValidationException, self).__init__(msg % code)
        self.traceback = ('', '', '')
