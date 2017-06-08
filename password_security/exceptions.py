# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp.exceptions import Warning as UserError


class PassError(UserError):
    """ Example: When you try to create an insecure password."""
    def __init__(self, msg):
        self.message = msg
        super(PassError, self).__init__(msg)
