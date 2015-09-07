from openerp.tests.common import TransactionCase
from openerp.osv.orm import except_orm


class TestBasics(TransactionCase):
    """ Check basic tag logic
    """

    def setUp(self):
        super(TestBasics, self).setUp()

        cr, uid = self.cr, self.uid

        self.tag_obj = self.registry('res.tag')
        self.tag_model_obj = self.registry('res.tag.model')
        self.tag_category_obj = self.registry('res.tag.category')
        self.test_obj = self.registry('res.tag.test.model')

        # Make test model taggable
        self.test_model_id = self.tag_model_obj.create(
            cr, uid, {'name': 'Test Model',
                      'model': 'res.tag.test.model'})

        # Create two records of test model
        self.test_1_id = self.test_obj.create(cr, uid, {'name': 'Test 1'})
        self.test_2_id = self.test_obj.create(cr, uid, {'name': 'Test 2'})

        # Create test tag category and tags
        self.test_tag_cat_id_1 = self.tag_category_obj.create(
            cr, uid, {'name': 'Tag Categ 1',
                      'code': 'tag_cat_1',
                      'model_id': self.test_model_id})
        self.test_tag_id_1 = self.tag_obj.create(
            cr, uid, {'name': 'TC1',
                      'code': 'tc1',
                      'model_id': self.test_model_id,
                      'category_id': self.test_tag_cat_id_1})
        self.test_tag_id_2 = self.tag_obj.create(
            cr, uid, {'name': 'TC2',
                      'code': 'tc2',
                      'model_id': self.test_model_id,
                      'category_id': self.test_tag_cat_id_1})
        self.test_tag_id_3 = self.tag_obj.create(
            cr, uid, {'name': 'TC3',
                      'code': 'tc3',
                      'model_id': self.test_model_id,
                      'category_id': False})

    def test_05_tags_count(self):
        model_tags_count = self.tag_model_obj.browse(
            self.cr, self.uid, self.test_model_id).tags_count
        self.assertEqual(model_tags_count, 3, "Wrong tags_count for model")
        category_tags_count = self.tag_category_obj.browse(
            self.cr, self.uid, self.test_tag_cat_id_1).tags_count
        self.assertEqual(category_tags_count, 2, "Wrong tags_count for model")

    def test_10_add_tag(self):
        """ Test that .add_tag method works fine
        """
        cr, uid = self.cr, self.uid

        # Test simple add
        res = self.test_obj.add_tag(cr, uid,
                                    self.test_1_id,
                                    name='Tag 1',
                                    code='Tag_1')
        test1 = self.test_obj.browse(cr, uid, self.test_1_id)
        self.assertEqual(res, False, "No tags must be added here")
        self.assertEqual(
            len(test1.tag_ids), 0,
            "There must be no tags added. (tag with such name does not exists")

        # Test simple add with create
        res = self.test_obj.add_tag(cr, uid,
                                    self.test_1_id,
                                    name='Tag 1',
                                    code='Tag_1',
                                    create=True)
        test1 = self.test_obj.browse(cr, uid, self.test_1_id)
        self.assertEqual(res, True, "There must be one tag created and added")
        self.assertEqual(
            len(test1.tag_ids), 1,
            "There are one tag must be present in object")
        self.assertEqual(test1.tag_ids[0].name, 'Tag 1')
        self.assertEqual(test1.tag_ids[0].code, 'Tag_1')

        # Try to add existing tag to existing object (use only code)
        res = self.test_obj.add_tag(cr, uid, self.test_2_id, code='Tag_1')
        test2 = self.test_obj.browse(cr, uid, self.test_2_id)
        self.assertEqual(res, True, "There must be one tag added")
        self.assertEqual(
            len(test2.tag_ids), 1,
            "There are one tag must be present in object")
        self.assertEqual(test2.tag_ids[0].name, 'Tag 1')
        self.assertEqual(test2.tag_ids[0].code, 'Tag_1')

        # Try to add tag to many objects at once
        res = self.test_obj.add_tag(cr, uid,
                                    [self.test_1_id, self.test_2_id],
                                    name='Tag 3',
                                    code='Tag_3',
                                    create=True)
        self.assertEqual(res, True, "There must be tag created and added")
        test1.refresh()
        test2.refresh()
        self.assertEqual(
            len(test1.tag_ids), 2,
            "There are two tags must be present in object")
        self.assertEqual(
            len(test2.tag_ids), 2,
            "There are two tags must be present in object")

    def test_20_check_tag(self):
        """ Test that .check_tag method works fine
        """
        cr, uid = self.cr, self.uid

        # First add tag to only one record
        self.test_obj.add_tag(cr, uid,
                              self.test_1_id,
                              name='Tag 1',
                              code='Tag_1',
                              create=True)

        # And check if it present there
        res = self.test_obj.check_tag(cr, uid,
                                      [self.test_1_id],
                                      name='Tag 1',
                                      code='Tag_1')
        self.assertEqual(res, True)

        # Then check for a list of records where only one record have specified
        # tag
        res = self.test_obj.check_tag(cr, uid,
                                      [self.test_1_id, self.test_2_id],
                                      name='Tag 1',
                                      code='Tag_1')
        self.assertEqual(res, False)

        # And check record without tags
        res = self.test_obj.check_tag(cr, uid,
                                      [self.test_2_id],
                                      name='Tag 1',
                                      code='Tag_1')
        self.assertEqual(res, False)

        # Check only by code
        res = self.test_obj.check_tag(cr, uid,
                                      [self.test_1_id],
                                      code='Tag_1')
        self.assertEqual(res, True)

        # Check only by name
        res = self.test_obj.check_tag(cr, uid, [self.test_1_id], name='Tag 1')
        self.assertEqual(res, True)

    def test_30_remove_tag(self):
        """ Test that .remove_tag method works fine
        """
        cr, uid = self.cr, self.uid

        # First add tag to only one record
        self.test_obj.add_tag(
            cr, uid, self.test_1_id, name='Tag 1', code='Tag_1', create=True)
        self.test_obj.add_tag(
            cr, uid, self.test_2_id, name='Tag 2', code='Tag_2', create=True)
        self.test_obj.add_tag(
            cr, uid, [self.test_1_id, self.test_2_id],
            name='Tag 3', code='Tag_3', create=True)

        # prepare browse_records
        test1 = self.test_obj.browse(cr, uid, self.test_1_id)
        test2 = self.test_obj.browse(cr, uid, self.test_2_id)

        # check preconditions
        self.assertEqual(len(test1.tag_ids), 2)
        self.assertEqual(len(test2.tag_ids), 2)

        # test .remove_tag on record without this tag
        self.test_obj.remove_tag(
            cr, uid, [self.test_1_id], name='Tag 2', code='Tag_2')
        test1.refresh()
        self.assertEqual(len(test1.tag_ids), 2)

        # test .remove_tag on recordset where one record have requested tag
        self.test_obj.remove_tag(
            cr, uid, [self.test_1_id, self.test_2_id],
            name='Tag 1', code='Tag_1')
        test1.refresh()
        test2.refresh()
        self.assertEqual(len(test1.tag_ids), 1)
        self.assertEqual(len(test2.tag_ids), 2)

        # test .remove_tag with unexisting tag, but name starts same as
        # existing
        self.test_obj.remove_tag(
            cr, uid, [self.test_1_id, self.test_2_id], name='Tag', code='Tag')
        test1.refresh()
        test2.refresh()
        self.assertEqual(len(test1.tag_ids), 1)
        self.assertEqual(len(test2.tag_ids), 2)

        # test .remove_tag method to remove tag present in all records in set
        self.test_obj.remove_tag(
            cr, uid, [self.test_1_id, self.test_2_id], name='Tag 3')
        test1.refresh()
        test2.refresh()
        self.assertEqual(len(test1.tag_ids), 0)
        self.assertEqual(len(test2.tag_ids), 1)

    def test_40_check_tag_category(self):
        """ Test if check tag category method works fine
        """
        cr, uid = self.cr, self.uid

        self.test_obj.add_tag(cr, uid, [self.test_1_id], code='tc1')
        self.test_obj.add_tag(
            cr, uid, [self.test_2_id],
            name='Test Tag1', code='Testtag1', create=True)

        res = self.test_obj.check_tag_category(
            cr, uid, [self.test_1_id], code='tag_cat_1')
        self.assertEqual(res, True)

        res = self.test_obj.check_tag_category(
            cr, uid, [self.test_2_id], code='tag_cat_1')
        self.assertEqual(res, False)

    def test_50_category_xor(self):
        """ Check that tag category xor logic works fine
        """
        cr, uid = self.cr, self.uid
        # prepare browse_records
        test1 = self.test_obj.browse(cr, uid, self.test_1_id)
        test2 = self.test_obj.browse(cr, uid, self.test_2_id)

        # Check that if category have no 'xor' check, then it is posible to add
        # more then one tag from this category to object
        self.test_obj.add_tag(
            cr, uid, [self.test_1_id, self.test_2_id], code='tc1')
        self.test_obj.add_tag(
            cr, uid, [self.test_1_id, self.test_2_id], code='tc2')
        test1.refresh()
        test2.refresh()
        self.assertEqual(len(test1.tag_ids), 2)
        self.assertEqual(len(test2.tag_ids), 2)

        # Remove tags from objects
        self.test_obj.remove_tag(
            cr, uid, [self.test_1_id, self.test_2_id], code='tc1')
        self.test_obj.remove_tag(
            cr, uid, [self.test_1_id, self.test_2_id], code='tc2')
        test1.refresh()
        test2.refresh()
        self.assertEqual(len(test1.tag_ids), 0)
        self.assertEqual(len(test2.tag_ids), 0)

        # Mark category as 'XOR'
        self.tag_category_obj.write(
            cr, uid, [self.test_tag_cat_id_1], {'check_xor': True})

        # And retry adding two tags from same category
        self.test_obj.add_tag(
            cr, uid, [self.test_1_id, self.test_2_id], code='tc1')
        with self.assertRaises(except_orm):
            self.test_obj.add_tag(
                cr, uid, [self.test_1_id, self.test_2_id], code='tc2')
