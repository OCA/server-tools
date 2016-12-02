# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.exceptions import AccessDenied


class MfaTokenError(AccessDenied):
    pass


class MfaTokenInvalidError(MfaTokenError):
    pass


class MfaTokenExpiredError(MfaTokenError):
    pass
