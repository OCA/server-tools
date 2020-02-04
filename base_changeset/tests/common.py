# Copyright 2015-2017 Camptocamp SA
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


class ChangesetTestCommon(object):
    def assert_changeset(self, record, expected_source, expected_changes):
        """ Check if a changeset has been created according to expected values

        The record should have no prior changeset than the one created in the
        test (so it has exactly 1 changeset).

        The expected changes are tuples with (field, origin_value,
        new_value, state)

        :param record: record of record having a changeset
        :param expected_changes: contains tuples with the changes
        :type expected_changes: list(tuple))
        """
        changeset = self.env["record.changeset"].search(
            [("model", "=", record._name), ("res_id", "=", record.id)]
        )
        self.assertEqual(
            len(changeset), 1, "1 changeset expected, got {}".format(changeset)
        )
        self.assertEqual(changeset.source, expected_source)
        changes = changeset.change_ids
        missing = []
        for expected_change in expected_changes:
            for change in changes:
                if (
                    change.field_id,
                    change.get_origin_value(),
                    change.get_new_value(),
                    change.state,
                ) == expected_change:
                    changes -= change
                    break
            else:
                missing.append(expected_change)
        message = ""
        for field, origin_value, new_value, state in missing:
            message += (
                "- field: '%s', origin_value: '%s', "
                "new_value: '%s', state: '%s'\n"
                % (field.name, origin_value, new_value, state)
            )
        for change in changes:
            message += (
                "+ field: '%s', origin_value: '%s', "
                "new_value: '%s', state: '%s'\n"
                % (
                    change.field_id.name,
                    change.get_origin_value(),
                    change.get_new_value(),
                    change.state,
                )
            )
        if message:
            raise AssertionError("Changes do not match\n\n:%s" % message)

    def _create_changeset(self, record, changes):
        """ Create a changeset and its associated changes

        :param record: 'record' record
        :param changes: list of changes [(field, new value, state)]
        :returns: 'record.changeset' record
        """
        ChangesetChange = self.env["record.changeset.change"]
        get_field = ChangesetChange.get_field_for_type
        change_values = []
        for field, value, state in changes:
            change = {
                "field_id": field.id,
                # write in the field of the appropriate type for the
                # origin field (char, many2one, ...)
                get_field(field, "new"): value,
                "state": state,
            }
            change_values.append((0, 0, change))
        values = {
            "model": record._name,
            "res_id": record.id,
            "change_ids": change_values,
        }
        return self.env["record.changeset"].create(values)
