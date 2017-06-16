# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import random
import string

from odoo.tests.common import TransactionCase

MAX_DB_USER_PARAM = 'user.threshold.database'


class Common(TransactionCase):

    def _create_test_user(self):
        """ Create a user for testing """
        user = self.env.ref('base.user_demo').copy()
        rand_name = ''.join([
            random.choice(string.ascii_letters) for n in xrange(10)
        ])
        user.write({'login': rand_name})
        return user

    def _add_user_to_group(self, user):
        """ Add a given user Record to the threshold manager group """
        th_group = self.env.ref('user_threshold.group_threshold_manager')
        system_group = self.env.ref('base.group_system')
        user.write({
            'in_group_%s' % th_group.id: True,
            'in_group_%s' % system_group.id: True
        })
