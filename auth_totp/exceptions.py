# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp.exceptions import AccessDenied


class MfaTokenError(AccessDenied):

    def __init__(self, message):
        super(MfaTokenError, self).__init__()
        self.message = message


class MfaTokenInvalidError(MfaTokenError):
    pass


class MfaTokenExpiredError(MfaTokenError):
    pass
