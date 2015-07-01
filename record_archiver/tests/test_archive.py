# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from datetime import datetime, timedelta
import openerp.tests.common as common


class TestArchive(common.TransactionCase):

    def setUp(self):
        super(TestArchive, self).setUp()
        self.Partner = self.registry('res.partner')
        cr, uid = self.cr, self.uid
        self.partner1_id = self.Partner.create(cr, uid,
                                               {'name': 'test user 1'})
        self.partner2_id = self.Partner.create(cr, uid,
                                               {'name': 'test user 2'})
        self.partner3_id = self.Partner.create(cr, uid,
                                               {'name': 'test user 3'})
        old_date = datetime.now() - timedelta(days=365)
        self.cr.execute('UPDATE res_partner SET write_date = %s '
                        'WHERE id IN %s', (old_date, tuple([self.partner2_id,
                                                            self.partner3_id]))
                        )
        self.Lifespan = self.registry('record.lifespan')
        self.model_id = self.ref('base.model_res_partner')

    def test_lifespan(self):
        cr, uid = self.cr, self.uid
        lifespan_id = self.Lifespan.create(
            cr, uid,
            {'model_id': self.model_id,
             'months': 3,
             })
        self.Lifespan.archive_records(cr, uid, [lifespan_id])
        self.assertTrue(self.Partner.browse(cr, uid, self.partner1_id).active)
        self.assertFalse(self.Partner.browse(cr, uid, self.partner2_id).active)
        self.assertFalse(self.Partner.browse(cr, uid, self.partner3_id).active)

    def test_scheduler(self):
        cr, uid = self.cr, self.uid
        self.Lifespan.create(
            cr, uid,
            {'model_id': self.model_id,
             'months': 3,
             })
        self.Lifespan._scheduler_archive_records(cr, uid)
        self.assertTrue(self.Partner.browse(cr, uid, self.partner1_id).active)
        self.assertFalse(self.Partner.browse(cr, uid, self.partner2_id).active)
        self.assertFalse(self.Partner.browse(cr, uid, self.partner3_id).active)
