# Copyright 2020 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestJsonifyMixin


class TestJsonifyExport(TestJsonifyMixin):
    def jsonify(self, record):
        parser = self.export.get_json_parser()
        return record.jsonify(parser)[0]

    def test_cron(self):
        """Basic cron that perform a recompute on all inherited models."""
        # given  # all records have to be recomputed
        cron = self.env.ref("jsonify_stored.recompute_all_jsonified")
        self.assertTrue(all(self.records.mapped("jsonify_data_todo")))

        # when
        cron.ir_actions_server_id.run()

        # then  # all records have been recomputed
        self.assertTrue(all(not t for t in self.records.mapped("jsonify_data_todo")))

    def test_write_export_fields(self):
        # given # let's start with everything computed
        self.assertEqual(self.record_1.jsonify_data, self.jsonify(self.record_1))
        self.assertEqual(self.record_2.jsonify_data, self.jsonify(self.record_2))
        self.assertTrue(all(not t for t in self.records.mapped("jsonify_data_todo")))

        # when  # we remove an export line from the export
        self.export.export_fields = self.export.export_fields[:-1]

        # then  # everything needs a recompute
        self.assertTrue(all(self.records.mapped("jsonify_data_todo")))

    def test_export(self):
        # given
        self.assertTrue(all(self.records.mapped("jsonify_data_todo")))

        # when  # we access stored data, no compute is performed
        json_data_stored = self.record_2.jsonify_data_stored
        # when  # we access fresh data, which should compute it
        json_data = self.record_1.jsonify_data

        # then
        self.assertEqual(json_data_stored, {})  # no value without recompute
        self.assertEqual(json_data, self.jsonify(self.record_1))
        self.assertFalse(self.record_1.jsonify_data_todo)
        self.assertTrue(self.record_2.jsonify_data_todo)

        # when  # same thing but with record_2
        json_data = self.record_2.jsonify_data

        # then
        self.assertEqual(json_data, self.jsonify(self.record_2))
        self.assertFalse(self.record_1.jsonify_data_todo)
        self.assertFalse(self.record_2.jsonify_data_todo)

        # when
        self.user_2.login = "newlogin"  # not part of the export
        # then  # it should not mark it for recomputation
        self.assertFalse(self.record_2.jsonify_data_todo)
        # when
        self.record_2.boolean = True
        # then  # it should mark 2 and 2 only for recomputation
        self.assertTrue(self.record_2.jsonify_data_todo)
        self.assertFalse(self.record_1.jsonify_data_todo)

    def test_create_write_unlink_export_line(self):
        # given # let's start with everything computed
        self.assertEqual(self.record_1.jsonify_data, self.jsonify(self.record_1))
        self.assertEqual(self.record_2.jsonify_data, self.jsonify(self.record_2))
        self.assertTrue(all(not t for t in self.records.mapped("jsonify_data_todo")))

        # when  # we modify an export line
        user_line = self.env.ref("test_jsonify_stored.model_export_line_user")
        user_line.name = "user_id/name"

        # then  # everything needs a recompute
        self.assertTrue(all(self.records.mapped("jsonify_data_todo")))
        # and we modified the model's depends
        field_depends = self.record_2._fields["jsonify_date_update"].depends
        model_depends = self.record_2._jsonify_get_export_depends()
        self.assertEqual(set(field_depends), set(model_depends))

        # given # let's start again with everything recomputed
        self.assertEqual(self.record_1.jsonify_data, self.jsonify(self.record_1))
        self.assertEqual(self.record_2.jsonify_data, self.jsonify(self.record_2))
        self.assertTrue(all(not t for t in self.records.mapped("jsonify_data_todo")))

        # when
        self.user_2.name = "newname"  # it's now part of the export

        # then  # it should now mark it for recomputation
        self.assertTrue(self.record_2.jsonify_data_todo)

        # given # let's start again with everything recomputed
        self.assertEqual(self.record_1.jsonify_data, self.jsonify(self.record_1))
        self.assertEqual(self.record_2.jsonify_data, self.jsonify(self.record_2))
        self.assertTrue(all(not t for t in self.records.mapped("jsonify_data_todo")))

        # when  # we create an export line
        new_user_line = user_line.copy({"name": "user_id/create_date"})

        # then  # everything needs a recompute
        self.assertTrue(all(self.records.mapped("jsonify_data_todo")))

        # given # let's start again with everything recomputed
        self.assertEqual(self.record_1.jsonify_data, self.jsonify(self.record_1))
        self.assertEqual(self.record_2.jsonify_data, self.jsonify(self.record_2))
        self.assertTrue(all(not t for t in self.records.mapped("jsonify_data_todo")))

        # when  # we remove an export line
        new_user_line.unlink()

        # then  # everything needs a recompute
        self.assertTrue(all(self.records.mapped("jsonify_data_todo")))
