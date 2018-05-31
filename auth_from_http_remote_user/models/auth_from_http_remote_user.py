# -*- coding: utf-8 -*-
# Copyright 2014-2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class AuthFromHttpRemoteUserInstalled(models.AbstractModel):
    """An abstract model used to safely know if the module is installed
    """
    _name = 'auth_from_http_remote_user.installed'
