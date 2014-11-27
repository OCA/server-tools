# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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
###############################################################################

from openerp.tests.common import TransactionCase


class TestDocumentExtractFromDatabase(TransactionCase):
    """Tests for 'Document Extract From Database' Module"""

    def setUp(self):
        super(TestDocumentExtractFromDatabase, self).setUp()
        self.icp_obj = self.registry('ir.config_parameter')
        self.ia_obj = self.registry('ir.attachment')
        self.dma_obj = self.registry('document.multiple.action')

    # Test Section
    def test_01_document_extract(self):
        """Test the correct extract of an attachment."""
        cr, uid = self.cr, self.uid
        # Make sure that Odoo is set to write attachment in Database
        self.icp_obj.unlink(cr, uid, self.icp_obj.search(
            cr, uid, [('key', '=', 'ir_attachment.location')]))

        # Create a new Attachment
        ia_id = self.ia_obj.create(cr, uid, {
            'name': 'Attachment Test',
            'datas_fname': 'pixel.png',
            'type': 'binary',
            'datas': """iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAABH"""
            """NCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAA1JREFUCJljO"""
            """LR/w38AB6kDMQ1kMu8AAAAASUVORK5CYII=""",
        })

        # Get Data Before
        data_before = self.ia_obj.browse(cr, uid, ia_id).datas
        # Change setting for attachment to save on filesystem
        self.icp_obj.create(cr, uid, {
            'key': 'ir_attachment.location',
            'value': 'file:///filestore',
        })

        # Run Write Again Functionnality
        self.dma_obj.write_again(cr, uid, 0, {'active_ids': [ia_id]})

        data_after = self.ia_obj.browse(cr, uid, ia_id).datas

        # Test if datas have not changed
        # Note: Replace \n char by nothing, because datas field are different
        # when ir_attachement is in Database or in File System
        ia = self.ia_obj.browse(cr, uid, ia_id)
        self.assertEqual(
            data_before, data_after.replace('\n', ''),
            "Datas have changed after exporting into filesystem.")

        # Test if the file is in the file system
        ia = self.ia_obj.browse(cr, uid, ia_id)
        self.assertNotEqual(
            ia.store_fname, None,
            "Attachment must be on File System after Write Again Function.")
