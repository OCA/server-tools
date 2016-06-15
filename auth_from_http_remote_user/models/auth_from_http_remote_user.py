# -*- coding: utf-8 -*-
# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models


class AuthFromHttpRemoteUserInstalled(models.AbstractModel):
    """An abstract model used to safely know if the module is installed
    """
    _name = 'auth_from_http_remote_user.installed'
