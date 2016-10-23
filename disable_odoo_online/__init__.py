# -*- coding: utf-8 -*-
# Copyright (C) 2013 Therp BV (<http://therp.nl>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from . import models

from odoo.tools.misc import upload_data_thread
upload_data_thread.run = lambda x: None
