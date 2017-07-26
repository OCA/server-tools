# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime
from psycopg2.extensions import AsIs
from dateutil.rrule import MONTHLY, rrule
from dateutil.tz import gettz
from openerp import SUPERUSER_ID, fields, models
from openerp.tests.common import TransactionCase
from ..field_rrule import FieldRRule, SerializableRRuleSet


class RRuleTest(models.TransientModel):
    _name = 'test.field.rrule'

    # either use a default in object notation
    rrule_with_default = FieldRRule(default=[{
        "type": "rrule",
        "dtstart": '2016-01-02 00:00:00',
        "count": 1,
        "freq": MONTHLY,
        "interval": 1,
        "bymonthday": [1],
    }])
    # or pass a SerializableRRuleSet.
    # Rember that this class is callable, so passing it directly as default
    # would actually pass an rruleset, because odoo uses the result of the
    # callable. But in __call__, we check for this case, so nothing to do
    rrule_with_default2 = FieldRRule(default=SerializableRRuleSet(
        rrule(
            dtstart=fields.Datetime.from_string('2016-01-02 00:00:00'),
            interval=1,
            freq=MONTHLY,
            count=1,
            bymonthday=[1],
        )))
    # also fiddle with an empty one
    rrule = FieldRRule()
    # and the timezone aware version
    rrule_with_tz = FieldRRule(stable_times=True)


class TestFieldRrule(TransactionCase):
    def test_field_rrule(self):
        model = RRuleTest._build_model(self.registry, self.cr)
        model._prepare_setup(self.cr, SUPERUSER_ID, False)
        model._setup_base(self.cr, SUPERUSER_ID, False)
        model._setup_fields(self.cr, SUPERUSER_ID)
        model._auto_init(self.cr)
        record_id = model.create(self.cr, SUPERUSER_ID, {'rrule': None})
        self.cr.execute(
            'select rrule, rrule_with_default, rrule_with_default2 from '
            '%s where id=%s', (AsIs(model._table), record_id))
        data = self.cr.fetchall()[0]
        self.assertEqual(data[0], 'null')
        self.assertEqual(data[1], data[2])
        record = model.browse(self.cr, SUPERUSER_ID, record_id)
        self.assertFalse(record.rrule)
        self.assertTrue(record.rrule_with_default)
        self.assertTrue(record.rrule_with_default2)
        self.assertEqual(record.rrule_with_default, record.rrule_with_default2)
        self.assertEqual(record.rrule_with_default.count(), 1)
        self.assertFalse(record.rrule_with_default.after(
            fields.Datetime.from_string('2016-02-01 00:00:00')))
        self.assertTrue(record.rrule_with_default.after(
            fields.Datetime.from_string('2016-02-01 00:00:00'), inc=True))
        record.env.user.write({'tz': 'Europe/Amsterdam'})
        record.rrule_with_tz = SerializableRRuleSet(
            rrule(
                dtstart=fields.Datetime.from_string('2017-02-02 23:00:00'),
                interval=1,
                freq=MONTHLY,
                count=2,
                bymonthday=[1],
            )
        )
        # this rruleset should receive Amsterdam as timezone, and should yield
        # different naive utc times depending on dst (NL switches in March)
        self.assertTrue(record.rrule_with_tz.tz)
        self.assertEqual(
            list(record.rrule_with_tz()),
            [
                datetime.datetime(2017, 2, 28, 23, 0),
                datetime.datetime(2017, 3, 31, 22, 0),
            ]
        )
        # doing the same with a timezone-aware datetime should work too
        record.rrule_with_tz = SerializableRRuleSet(
            rrule(
                dtstart=fields.Datetime.from_string('2017-02-03 00:00:00')
                .replace(tzinfo=gettz('Europe/Amsterdam')),
                interval=1,
                freq=MONTHLY,
                count=2,
                bymonthday=[1],
            )
        )
        self.assertTrue(record.rrule_with_tz.tz)
        self.assertEqual(
            list(record.rrule_with_tz()),
            [
                datetime.datetime(2017, 2, 28, 23, 0),
                datetime.datetime(2017, 3, 31, 22, 0),
            ]
        )
        # and the same again with the json representation
        record.rrule_with_tz = [
            {
                'type': 'rrule',
                'dtstart': '2017-02-02 23:00:00',
                'interval': 1,
                'freq': MONTHLY,
                'count': 2,
                'bymonthday': [1],
            },
            {
                'type': 'tz',
                'tz': 'Europe/Amsterdam',
            }
        ]
        self.assertTrue(record.rrule_with_tz.tz)
        self.assertEqual(
            list(record.rrule_with_tz()),
            [
                datetime.datetime(2017, 2, 28, 23, 0),
                datetime.datetime(2017, 3, 31, 22, 0),
            ]
        )
