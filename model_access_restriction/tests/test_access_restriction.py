# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase
from odoo import exceptions


class TestAccessRestriction(TransactionCase):
    """
    Tests for access.restriction model
    """

    def setUp(self):
        super(TestAccessRestriction, self).setUp()
        self.restriction_obj = self.env['access.restriction']
        # Disable tracking, mail follower etc
        self.partner_obj = self.env['res.partner'].with_context(
            mail_create_nosubscribe=True,
            mail_create_nolog=True,
            mail_notrack=True)
        self.user_obj = self.env['res.users']
        self.group_obj = self.env['res.groups']
        self.model_obj = self.env['ir.model']
        self.user_demo = self.env.ref("base.user_demo")
        self.user2 = self.user_obj.create({
            'name': 'My twin',
            'login': 'twintwin',
            'email': 'twintwin@example.com',
        })
        # We have to disable every others rules to avoid issue during these
        # unit test
        self.restriction_obj.search([]).write({
            'active': False,
        })

    def _create_rule(self, model, groups, read=False, create=False,
                     write=False, unlink=False, active=True):
        """
        Create a new access.restriction rule based on given parameters
        :param model: ir.model recordset
        :param groups: res.groups recordset
        :param read: bool
        :param create: bool
        :param write: bool
        :param unlink: bool
        :return: access.restriction recordset
        """
        values = {
            'name': 'A restriction access name - Unit test',
            'ir_model_id': model.id,
            'perm_create': create,
            'perm_read': read,
            'perm_write': write,
            'perm_unlink': unlink,
            'active': active,
            'res_group_ids': [(6, False, groups.ids)],
        }
        return self.restriction_obj.sudo().create(values)

    def _create_group(self, name, users=False):
        """
        Create a group with given name.
        Add given users into the group.
        :param name: str
        :param users: res.users recordset
        :return:
        """
        if not users:
            users = self.user_obj.browse()
        values = {
            'name': name,
            'users': [(6, False, users.ids)]
        }
        return self.group_obj.sudo().create(values)

    def test_access_restriction_rule_read1(self):
        """
        Create a new access.restriction rule to check if this rule is
        correctly applied.
        In this case, we test the read access
        :return: bool
        """
        partner_model = self.model_obj.search([
            ('model', '=', self.partner_obj._name)], limit=1)
        group = self._create_group("A new group", users=self.user2)
        rule = self._create_rule(partner_model, group, read=True)
        exception_message = "Access denied.\nPlease contact your " \
                            "administrator or check your access restriction " \
                            "rules."
        with self.assertRaises(exceptions.AccessError) as e:
            self.partner_obj.sudo(self.user_demo).search([], limit=1)
        self.assertEquals(e.exception.name, exception_message)
        # The other user should have access because he is into the group
        self.partner_obj.sudo(self.user2).search([], limit=1)
        rule.write({
            'active': False,
        })
        # Rule disabled, should work
        self.partner_obj.sudo(self.user_demo).search([], limit=1)
        # Even for second user
        self.partner_obj.sudo(self.user2).search([], limit=1)
        # Now enable the rule but disable read restriction
        rule.write({
            'active': True,
            'perm_read': False,
        })
        # Read restriction disable so it should work
        self.partner_obj.sudo(self.user_demo).search([], limit=1)
        self.partner_obj.sudo(self.user2).search([], limit=1)
        # Now re-enable read restriction but add the user into the group
        rule.write({
            'perm_read': True,
        })
        group.write({
            'users': [(6, False, self.user_demo.ids)],
        })
        # Should work due to group allowed
        self.partner_obj.sudo(self.user_demo).search([], limit=1)
        # The second user doesn't have access anymore
        with self.assertRaises(exceptions.AccessError) as e:
            self.partner_obj.sudo(self.user2).search([], limit=1)
        self.assertEquals(e.exception.name, exception_message)
        # Now test if the rule is correctly apply in case of multi-group
        group2 = self._create_group("Another new group")
        rule.write({
            'res_group_ids': [(4, group2.id, False)],
        })
        # Should work because the user is into the first group
        self.partner_obj.sudo(self.user_demo).search([], limit=1)
        # Remove the user from the first group
        group.write({
            'users': [(6, False, [])],
        })
        # Should have an exception
        with self.assertRaises(exceptions.AccessError) as e:
            self.partner_obj.sudo(self.user_demo).search([], limit=1)
        self.assertEquals(e.exception.name, exception_message)
        with self.assertRaises(exceptions.AccessError) as e:
            self.partner_obj.sudo(self.user2).search([], limit=1)
        self.assertEquals(e.exception.name, exception_message)
        # Add user into the second group
        group2.write({
            'users': [(4, self.user_demo.id), (4, self.user2.id)],
        })
        # And it should work
        self.partner_obj.sudo(self.user_demo).search([], limit=1)
        self.partner_obj.sudo(self.user2).search([], limit=1)
        return True

    def test_access_restriction_rule_create1(self):
        """
        Create a new access.restriction rule to check if this rule is
        correctly applied.
        In this case, we test the create access
        :return: bool
        """
        partner_model = self.model_obj.search([
            ('model', '=', self.partner_obj._name)], limit=1)
        group = self._create_group("A new group", users=self.user2)
        rule = self._create_rule(partner_model, group, create=True)
        exception_message = "Access denied.\nPlease contact your " \
                            "administrator or check your access restriction " \
                            "rules."
        partner_values = {
            'name': 'My partner name',
        }
        with self.assertRaises(exceptions.AccessError) as e:
            self.partner_obj.sudo(self.user_demo).create(partner_values)
        self.assertEquals(e.exception.name, exception_message)
        partner = self.partner_obj.sudo(self.user2).create(partner_values)
        partner.unlink()
        rule.write({
            'active': False,
        })
        # Rule disabled, should work
        partner = self.partner_obj.sudo(self.user_demo).create(partner_values)
        # Delete the partner in case of another module add some restriction
        # To create the same partner later
        partner.unlink()
        partner = self.partner_obj.sudo(self.user2).create(partner_values)
        partner.unlink()
        # Now enable the rule but disable create restriction
        rule.write({
            'active': True,
            'perm_create': False,
        })
        # Create restriction disable so it should work
        partner = self.partner_obj.sudo(self.user_demo).create(partner_values)
        partner.unlink()
        partner = self.partner_obj.sudo(self.user2).create(partner_values)
        partner.unlink()
        # Now re-enable create restriction but add the user into the group
        rule.write({
            'perm_create': True,
        })
        group.write({
            'users': [(6, False, self.user_demo.ids)],
        })
        # Should work due to group allowed
        partner = self.partner_obj.sudo(self.user_demo).create(partner_values)
        partner.unlink()
        with self.assertRaises(exceptions.AccessError) as e:
            self.partner_obj.sudo(self.user2).create(partner_values)
        self.assertEquals(e.exception.name, exception_message)
        # Now test if the rule is correctly apply in case of multi-group
        group2 = self._create_group("Another new group")
        rule.write({
            'res_group_ids': [(4, group2.id, False)],
        })
        # Should work because the user is into the first group
        partner = self.partner_obj.sudo(self.user_demo).create(partner_values)
        partner.unlink()
        with self.assertRaises(exceptions.AccessError) as e:
            self.partner_obj.sudo(self.user2).create(partner_values)
        self.assertEquals(e.exception.name, exception_message)
        # Remove the user from the first group
        group.write({
            'users': [(6, False, [])],
        })
        # Should have an exception
        with self.assertRaises(exceptions.AccessError) as e:
            self.partner_obj.sudo(self.user_demo).create(partner_values)
        self.assertEquals(e.exception.name, exception_message)
        with self.assertRaises(exceptions.AccessError) as e:
            self.partner_obj.sudo(self.user2).create(partner_values)
        self.assertEquals(e.exception.name, exception_message)
        # Add user into the second group
        group2.write({
            'users': [(4, self.user_demo.id), (4, self.user2.id)],
        })
        # And it should work
        partner = self.partner_obj.sudo(self.user_demo).create(partner_values)
        partner.unlink()
        partner = self.partner_obj.sudo(self.user2).create(partner_values)
        partner.unlink()
        return True

    def test_access_restriction_rule_write1(self):
        """
        Create a new access.restriction rule to check if this rule is
        correctly applied.
        In this case, we test the write access
        :return: bool
        """
        partner_model = self.model_obj.search([
            ('model', '=', self.partner_obj._name)], limit=1)
        group = self._create_group("A new group", users=self.user2)
        rule = self._create_rule(partner_model, group, write=True)
        exception_message = "Access denied.\nPlease contact your " \
                            "administrator or check your access restriction " \
                            "rules."
        partner = self.partner_obj.create({
            'name': 'My partner name',
        })
        partner_values = {
            'name': 'My new partner name',
        }
        with self.assertRaises(exceptions.AccessError) as e:
            partner.sudo(self.user_demo).write(partner_values)
        self.assertEquals(e.exception.name, exception_message)
        partner.sudo(self.user2).write(partner_values)
        rule.write({
            'active': False,
        })
        # Rule disabled, should work
        partner.sudo(self.user_demo).write(partner_values)
        partner.sudo(self.user2).write(partner_values)
        # Now enable the rule but disable write restriction
        rule.write({
            'active': True,
            'perm_write': False,
        })
        # Write restriction disable so it should work
        partner.sudo(self.user_demo).write(partner_values)
        partner.sudo(self.user2).write(partner_values)
        # Now re-enable write restriction but add the user into the group
        rule.write({
            'perm_write': True,
        })
        group.write({
            'users': [(6, False, self.user_demo.ids)],
        })
        # Should work due to group allowed
        partner.sudo(self.user_demo).write(partner_values)
        with self.assertRaises(exceptions.AccessError) as e:
            partner.sudo(self.user2).write(partner_values)
        self.assertEquals(e.exception.name, exception_message)
        # Now test if the rule is correctly apply in case of multi-group
        group2 = self._create_group("Another new group")
        rule.write({
            'res_group_ids': [(4, group2.id, False)],
        })
        # Should work because the user is into the first group
        partner.sudo(self.user_demo).write(partner_values)
        with self.assertRaises(exceptions.AccessError) as e:
            partner.sudo(self.user2).write(partner_values)
        self.assertEquals(e.exception.name, exception_message)
        # Remove the user from the first group
        group.write({
            'users': [(6, False, [])],
        })
        # Should have an exception
        with self.assertRaises(exceptions.AccessError) as e:
            partner.sudo(self.user_demo).write(partner_values)
        self.assertEquals(e.exception.name, exception_message)
        with self.assertRaises(exceptions.AccessError) as e:
            partner.sudo(self.user2).write(partner_values)
        self.assertEquals(e.exception.name, exception_message)
        # Add user into the second group
        group2.write({
            'users': [(4, self.user_demo.id), (4, self.user2.id)],
        })
        # And it should work
        partner.sudo(self.user_demo).write(partner_values)
        partner.sudo(self.user2).write(partner_values)
        return True

    def test_access_restriction_rule_unlink1(self):
        """
        Create a new access.restriction rule to check if this rule is
        correctly applied.
        In this case, we test the unlink access
        :return: bool
        """
        partner_model = self.model_obj.search([
            ('model', '=', self.partner_obj._name)], limit=1)
        group = self._create_group("A new group", users=self.user2)
        rule = self._create_rule(partner_model, group, unlink=True)
        exception_message = "Access denied.\nPlease contact your " \
                            "administrator or check your access restriction " \
                            "rules."
        partner_values = {
            'name': 'My partner name',
        }
        partner = self.partner_obj.create(partner_values)
        with self.assertRaises(exceptions.AccessError) as e:
            partner.sudo(self.user_demo).unlink()
        self.assertEquals(e.exception.name, exception_message)
        self.assertTrue(partner.exists())
        partner.sudo(self.user2).unlink()
        partner = self.partner_obj.create(partner_values)
        rule.write({
            'active': False,
        })
        # Rule disabled, should work
        partner.sudo(self.user_demo).unlink()
        self.assertFalse(partner.exists())
        partner = self.partner_obj.create(partner_values)
        partner.sudo(self.user2).unlink()
        partner = self.partner_obj.create(partner_values)
        # Now enable the rule but disable unlink restriction
        rule.write({
            'active': True,
            'perm_unlink': False,
        })
        # Unlink restriction disable so it should work
        partner.sudo(self.user_demo).unlink()
        self.assertFalse(partner.exists())
        partner = self.partner_obj.create(partner_values)
        partner.sudo(self.user2).unlink()
        self.assertFalse(partner.exists())
        partner = self.partner_obj.create(partner_values)
        # Now re-enable write restriction but add the user into the group
        rule.write({
            'perm_unlink': True,
        })
        group.write({
            'users': [(6, False, self.user_demo.ids)],
        })
        # Should work due to group allowed
        partner.sudo(self.user_demo).unlink()
        self.assertFalse(partner.exists())
        partner = self.partner_obj.create(partner_values)
        with self.assertRaises(exceptions.AccessError) as e:
            partner.sudo(self.user2).unlink()
        self.assertEquals(e.exception.name, exception_message)
        self.assertTrue(partner.exists())
        # Now test if the rule is correctly apply in case of multi-group
        group2 = self._create_group("Another new group")
        rule.write({
            'res_group_ids': [(4, group2.id, False)],
        })
        # Should work because the user is into the first group
        partner.sudo(self.user_demo).unlink()
        self.assertFalse(partner.exists())
        partner = self.partner_obj.create(partner_values)
        with self.assertRaises(exceptions.AccessError) as e:
            partner.sudo(self.user2).unlink()
        self.assertEquals(e.exception.name, exception_message)
        self.assertTrue(partner.exists())
        # Remove the user from the first group
        group.write({
            'users': [(6, False, [])],
        })
        # Should have an exception
        with self.assertRaises(exceptions.AccessError) as e:
            partner.sudo(self.user_demo).unlink()
        self.assertEquals(e.exception.name, exception_message)
        self.assertTrue(partner.exists())
        with self.assertRaises(exceptions.AccessError) as e:
            partner.sudo(self.user2).unlink()
        self.assertEquals(e.exception.name, exception_message)
        self.assertTrue(partner.exists())
        # Add user into the second group
        group2.write({
            'users': [(4, self.user_demo.id), (4, self.user2.id)],
        })
        # And it should work
        partner.sudo(self.user_demo).unlink()
        self.assertFalse(partner.exists())
        partner = self.partner_obj.create(partner_values)
        partner.sudo(self.user2).unlink()
        self.assertFalse(partner.exists())
        return True
