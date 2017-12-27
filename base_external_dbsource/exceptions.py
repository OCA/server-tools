# -*- coding: utf-8 -*-
# Copyright 2011 Daniel Reis, Maxime Chambreuil, Savoir-faire Linux
# Copyright 2016 LasLabs Inc.
# Copyright 2017 Henry Zhou <zhouhenry@live.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError


class ConnectionFailedError(UserError):
    pass


class ConnectionSuccessError(UserError):
    pass
