# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from contextlib import contextmanager
import odoo.tests.common as common


class TestOnchangeHelper(common.TransactionCase):
    def setUp(self):
        super(TestOnchangeHelper, self).setUp()
        self.Category = self.env["test_onchange_helper.category"]
        self.Message = self.env["test_onchange_helper.message"]
        self.Discussion = self.env["test_onchange_helper.discussion"]

    @contextmanager
    def assertNoOrmWrite(self, model):
        with mock.patch.object(
            model.__class__, "create"
        ) as mocked_create, mock.patch.object(
            model.__class__, "write"
        ) as mocked_write:
            yield
            mocked_create.assert_not_called()
            mocked_write.assert_not_called()

    def test_play_onhanges_no_recompute(self):
        # play_onchanges must not trigger recomputes except if an onchange
        # method access a computed field.
        # changing 'discussion' should recompute 'name'
        values = {"name": "Cat Name"}
        self.env.invalidate_all()
        with self.assertNoOrmWrite(self.Category):
            result = self.Category.play_onchanges(values, ["name"])
        self.assertNotIn("computed_display_name", result)

    def test_play_onchanges_many2one_new_record(self):
        root = self.Category.create({"name": "root"})

        values = {"name": "test", "parent": root.id, "root_categ": False}

        self.env.invalidate_all()
        with self.assertNoOrmWrite(self.Category):
            result = self.Category.play_onchanges(values, "parent")
        self.assertIn("root_categ", result)
        self.assertEqual(result["root_categ"], root.id)

        values.update(result)
        values["parent"] = False

        self.env.invalidate_all()
        with self.assertNoOrmWrite(self.Category):
            result = self.Category.play_onchanges(values, "parent")
        # since the root_categ is already False into values the field is not
        # changed by the onchange
        self.assertNotIn("root_categ", result)

    def test_play_onchanges_many2one_existing_record(self):
        root = self.Category.create({"name": "root"})

        values = {"name": "test", "parent": root.id, "root_categ": False}

        self.env.invalidate_all()
        with self.assertNoOrmWrite(self.Category):
            result = self.Category.play_onchanges(values, "parent")
        self.assertIn("root_categ", result)
        self.assertEqual(result["root_categ"], root.id)

        # create child catefory
        values.update(result)
        child = self.Category.create(values)
        self.assertEqual(root.id, child.root_categ.id)

        # since the parent is set to False and the root_categ
        values = {"parent": False}
        self.env.invalidate_all()
        with self.assertNoOrmWrite(child):
            result = child.play_onchanges(values, "parent")

        self.assertIn("root_categ", result)
        self.assertEqual(result["root_categ"], False)

    def test_play_onchange_one2many_new_record(self):
        """ test the effect of play_onchanges() on one2many fields on new
        record"""
        BODY = "What a beautiful day!"
        USER = self.env.user

        # create an independent message
        message = self.Message.create({"body": BODY})

        # modify discussion name
        values = {
            "name": "Foo",
            "categories": [],
            "moderator": False,
            "participants": [],
            "messages": [
                (4, message.id),
                (
                    0,
                    0,
                    {
                        "name": "[%s] %s" % ("", USER.name),
                        "body": BODY,
                        "author": USER.id,
                        "important": False,
                    },
                ),
            ],
        }
        self.env.invalidate_all()
        with self.assertNoOrmWrite(self.Discussion):
            result = self.Discussion.play_onchanges(values, "name")
        self.assertIn("messages", result)
        self.assertItemsEqual(
            result["messages"],
            [
                (5,),
                (
                    1,
                    message.id,
                    {
                        "name": "[%s] %s" % ("Foo", USER.name),
                        "body": "not last dummy message",
                        "author": message.author.id,
                        "important": message.important,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "[%s] %s" % ("Foo", USER.name),
                        "body": "not last dummy message",
                        "author": USER.id,
                        "important": False,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "[%s] %s" % ("Foo", USER.name),
                        "body": "dummy message",
                        "author": USER.id,
                        "important": True,
                    },
                ),
            ],
        )

        self.assertIn("important_messages", result)
        self.assertItemsEqual(
            result["important_messages"],
            [
                (5,),
                (
                    0,
                    0,
                    {
                        "author": USER.id,
                        "body": "dummy message",
                        "important": True,
                    },
                ),
            ],
        )

    def test_play_onchange_one2many_existing_record(self):
        """ test the effect of play_onchanges() on one2many fields on existing
        record"""
        BODY = "What a beautiful day!"
        USER = self.env.user

        # create an independent message
        message = self.Message.create({"body": BODY})

        # modify discussion name
        values = {
            "name": "Foo",
            "categories": [],
            "moderator": False,
            "participants": [],
            "messages": [
                (4, message.id),
                (
                    0,
                    0,
                    {
                        "name": "[%s] %s" % ("", USER.name),
                        "body": BODY,
                        "author": USER.id,
                        "important": False,
                    },
                ),
            ],
        }
        discussion = self.Discussion.create(values)

        values = {"name": "New foo"}
        with self.assertNoOrmWrite(discussion):
            result = discussion.play_onchanges(values, "name")
        self.assertIn("messages", result)
        self.assertItemsEqual(
            result["messages"],
            [
                (5,),
                (
                    1,
                    discussion.messages[0].id,
                    {
                        "name": "[%s] %s" % ("New foo", USER.name),
                        "body": "not last dummy message",
                        "author": message.author.id,
                        "important": message.important,
                        "discussion": discussion.id,
                    },
                ),
                (
                    1,
                    discussion.messages[1].id,
                    {
                        "name": "[%s] %s" % ("New foo", USER.name),
                        "body": "not last dummy message",
                        "author": USER.id,
                        "important": False,
                        "discussion": discussion.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "[%s] %s" % ("New foo", USER.name),
                        "body": "dummy message",
                        "author": USER.id,
                        "important": True,
                        "discussion": discussion.id,
                    },
                ),
            ],
        )

        self.assertIn("important_messages", result)
        self.assertItemsEqual(
            result["important_messages"],
            [
                (5,),
                (
                    0,
                    0,
                    {
                        "author": USER.id,
                        "body": "dummy message",
                        "important": True,
                        "discussion": discussion.id,
                    },
                ),
            ],
        )

    def test_onchange_specific(self):
        """test that only the id is added if a new item is added to an
        existing relation"""
        discussion = self.env.ref("test_onchange_helper.discussion_demo_0")
        demo = self.env.ref("base.user_demo")

        # first remove demo user from participants
        discussion.participants -= demo
        self.assertNotIn(demo, discussion.participants)

        # check that demo_user is added to participants when set as moderator
        values = {
            "name": discussion.name,
            "moderator": demo.id,
            "categories": [(4, cat.id) for cat in discussion.categories],
            "messages": [(4, msg.id) for msg in discussion.messages],
            "participants": [(4, usr.id) for usr in discussion.participants],
        }
        self.env.invalidate_all()
        with self.assertNoOrmWrite(discussion):
            result = discussion.play_onchanges(values, "moderator")

        self.assertIn("participants", result)
        self.assertItemsEqual(
            result["participants"],
            [(5,)] + [(4, user.id) for user in discussion.participants + demo],
        )

    def test_onchange_one2many_value(self):
        """ test that the values provided for a one2many field inside are used
        by the play_onchanges  """
        discussion = self.env.ref("test_onchange_helper.discussion_demo_0")
        demo = self.env.ref("base.user_demo")

        self.assertEqual(len(discussion.messages), 3)
        messages = [(4, msg.id) for msg in discussion.messages]
        messages[0] = (1, messages[0][1], {"body": "test onchange"})
        values = {
            "name": discussion.name,
            "moderator": demo.id,
            "categories": [(4, cat.id) for cat in discussion.categories],
            "messages": messages,
            "participants": [(4, usr.id) for usr in discussion.participants],
            "message_concat": False,
        }
        with self.assertNoOrmWrite(discussion):
            result = discussion.play_onchanges(values, "messages")
        self.assertIn("message_concat", result)
        self.assertEqual(
            result["message_concat"],
            "\n".join(
                ["%s:%s" % (m.name, m.body) for m in discussion.messages]
            ),
        )

    def test_onchange_one2many_line(self):
        """ test that changes on a field used as first position into the
        related path of a related field will trigger the onchange also on the
        related field """
        partner = self.env.ref("base.res_partner_1")
        multi = self.env["test_onchange_helper.multi"].create(
            {"partner": partner.id}
        )
        line = multi.lines.create({"multi": multi.id})

        values = multi._convert_to_write(
            {key: multi[key] for key in ("partner", "lines")}
        )
        self.assertEqual(
            values, {"partner": partner.id, "lines": [(6, 0, [line.id])]}
        )

        # modify 'partner'
        #   -> set 'partner' on all lines
        #   -> recompute 'name' (related on partner)
        #       -> set 'name' on all lines
        partner = self.env.ref("base.res_partner_2")
        values = {
            "partner": partner.id,
            "lines": [
                (6, 0, [line.id]),
                (0, 0, {"name": False, "partner": False}),
            ],
        }

        self.env.invalidate_all()
        with self.assertNoOrmWrite(multi):
            result = multi.play_onchanges(values, "partner")
        self.assertEqual(
            result,
            {
                "name": partner.name,
                "lines": [
                    (5,),
                    (
                        1,
                        line.id,
                        {
                            "name": partner.name,
                            "partner": partner.id,
                            "multi": multi.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": partner.name,
                            "partner": partner.id,
                            "multi": multi.id,
                        },
                    ),
                ],
            },
        )
