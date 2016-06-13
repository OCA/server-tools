"""Utilities useful to Odoo tests.
"""

import openerp.models
import openerp.tests


class TestBase(openerp.tests.SingleTransactionCase):
    """Provide some test helpers.
    """

    def createAndTest(self, model, value_list):
        """Create records of the specified Odoo model using the specified
        values, and ensure afterwards that records have been succesfully
        created and that their values are the same as expected.

        :return: The created records.
        :rtype: List of openerp.models.BaseModel instances.
        """

        records = []

        for values in value_list:

            # Maintain a local copy as Odoo calls might modify it...
            local_values = values.copy()

            record = self.env[model].create(values)
            records.append(record)

            self.assertIsInstance(record, openerp.models.BaseModel)

            for field, value in local_values.iteritems():

                recorded_value = getattr(record, field)

                # Handle relational fields (Odoo record-sets).
                if isinstance(recorded_value, openerp.models.BaseModel):
                    if isinstance(recorded_value, (tuple, list)):
                        self.assertEqual(recorded_value.ids, value)
                    else:
                        self.assertEqual(recorded_value.id, value)

                else:
                    self.assertEqual(recorded_value, value)

        return records
