from openerp import SUPERUSER_ID
from openerp.tests import common


class base_action_rule_test(common.TransactionCase):

    def setUp(self):
        """*****setUp*****"""
        super(base_action_rule_test, self).setUp()
        cr, uid = self.cr, self.uid
        self.tag_obj = self.registry('res.tag')
        self.tag_model_obj = self.registry('res.tag.model')
        self.tag_category_obj = self.registry('res.tag.category')
        self.test_obj = self.registry('res.tag.test.model')
        self.action_rule_obj = self.registry('base.action.rule')

        # Make test model taggable
        self.test_model_id = self.tag_model_obj.create(cr, uid, {'name': 'Test Model',
                                                                 'model': 'res.tag.test.model'})

        # Create two records of test model
        self.test_1_id = self.test_obj.create(cr, uid, {'name': 'Test 1'})
        self.test_2_id = self.test_obj.create(cr, uid, {'name': 'Test 2'})

        # Create test tag category and tags
        self.test_tag_cat_id_1 = self.tag_category_obj.create(cr, uid, {'name': 'Tag Categ 1',
                                                                        'model_id': self.test_model_id})
        self.test_tag_id_1 = self.tag_obj.create(cr, uid, {'name': 'TC1',
                                                           'code': 'tc1',
                                                           'model_id': self.test_model_id,
                                                           'category_id': self.test_tag_cat_id_1})
        self.test_tag_id_2 = self.tag_obj.create(cr, uid, {'name': 'TC2',
                                                           'code': 'tc2',
                                                           'model_id': self.test_model_id,
                                                           'category_id': self.test_tag_cat_id_1})

        # Basic action rules config
        self.filter_add_id = self.registry('ir.filters').create(cr, uid, {
            'name': "Test model test field = 'add'",
            'is_default': False,
            'model_id': 'res.tag.test.model',
            'domain': "[('test_field','=','add')]",
        })
        self.filter_rem_id = self.registry('ir.filters').create(cr, uid, {
            'name': "Test model test field = 'remove'",
            'is_default': False,
            'model_id': 'res.tag.test.model',
            'domain': "[('test_field','=','remove')]",
        })
        self.action_rule_id_1 = self.action_rule_obj.create(cr, uid, {
            'name': "Rule auto add tag",
            'model_id': self.registry('ir.model').search(cr, uid, [('model', '=', 'res.tag.test.model')])[0],
            'active': 1,
            #'filter_pre_id': filter_pre_id,
            'filter_id': self.filter_add_id,
            'act_add_tag_ids': [(4, self.test_tag_id_1)],
            'kind': 'on_create_or_write',
        })
        self.action_rule_id_2 = self.action_rule_obj.create(cr, uid, {
            'name': "Rule auto remove tag",
            'model_id': self.registry('ir.model').search(cr, uid, [('model', '=', 'res.tag.test.model')])[0],
            'active': 1,
            #'filter_pre_id': filter_pre_id,
            'filter_id': self.filter_rem_id,
            'act_remove_tag_ids': [(4, self.test_tag_id_1)],
            'kind': 'on_create_or_write',
        })

    def test_10_rules_created_right(self):
        """ Test that rules were created correctly
        """
        cr, uid = self.cr, self.uid
        rule1 = self.action_rule_obj.browse(cr, uid, self.action_rule_id_1)
        rule2 = self.action_rule_obj.browse(cr, uid, self.action_rule_id_2)

        self.assertEquals(rule1.act_add_tag_ids[0].id, self.test_tag_id_1)
        self.assertEquals(len(rule1.act_remove_tag_ids), 0)
        self.assertEquals(len(rule2.act_add_tag_ids), 0)
        self.assertEquals(rule2.act_remove_tag_ids[0].id, self.test_tag_id_1)

    def test_20_test_rule_actions(self):
        """ Test that rule_actions work fine
        """
        cr, uid = self.cr, self.uid

        test1 = self.test_obj.browse(cr, uid, self.test_1_id)
        self.assertEquals(len(test1.tag_ids), 0)

        # Test that act_add_field works fine
        test1.write({'test_field': 'add'})
        test1.refresh()
        self.assertEquals(test1.test_field, 'add')
        self.assertEquals(len(test1.tag_ids), 1)
        self.assertEquals(test1.tag_ids[0].name, 'TC1')

        # Add another tag to object
        test1.add_tag(name='TC2')
        test1.refresh()
        self.assertEquals(len(test1.tag_ids), 2)

        # Test that act_rem_field works fine
        test1.write({'test_field': 'remove'})
        test1.refresh()
        self.assertEquals(test1.test_field, 'remove')
        self.assertEquals(len(test1.tag_ids), 1)
        self.assertEquals(test1.tag_ids[0].name, 'TC2')
