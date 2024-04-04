# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from freezegun import freeze_time

import odoo
from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class TestDST(TransactionCase):
    def setUp(self):
        super().setUp()
        self.registry.enter_test_mode(self.env.cr)

    def tearDown(self):
        self.registry.leave_test_mode()
        super().tearDown()

    def _check_cron_date_after_run(self, cron, datetime_str):
        # add 10 sec to make sure cron will run
        datetime_current = datetime.strptime(
            datetime_str, DEFAULT_SERVER_DATETIME_FORMAT
        ) + timedelta(seconds=10)
        datetime_current_str = datetime_current.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        with freeze_time(datetime_current_str):
            cron.write(
                {"nextcall": datetime_str, "daylight_saving_time_resistant": True}
            )
            cron.flush_recordset()
            cron.ir_actions_server_id.flush_recordset(
                fnames=[
                    "model_name",
                ],
            )
            self.env.cr.execute("SELECT * FROM ir_cron WHERE id = %s", (cron.id,))
            job = self.env.cr.dictfetchall()[0]
            timezone_date_orig = fields.Datetime.context_timestamp(cron, cron.nextcall)
            # ensure Paris time zone is taken into account. If we only work in UTC
            # there is not change of hour and the test will be green even if it does
            # nothing at all...
            self.assertEqual(timezone_date_orig.tzinfo.zone, "Europe/Paris")
            with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                registry = odoo.registry(new_cr.dbname)
                db = odoo.sql_db.db_connect(new_cr.dbname)

                registry["ir.cron"]._process_job(db, new_cr, job)
                # since it is updated as a sql query in module
                cron.invalidate_recordset()
                day_after_date_orig = (timezone_date_orig + timedelta(days=1)).day
            timezone_date_after = fields.Datetime.context_timestamp(cron, cron.nextcall)
            # check the cron is really planned the next day (which mean it has run
            # then check the planned hour is the same even in case of change of time
            # (brussels summer time/ brussels winter time
            self.assertEqual(day_after_date_orig, timezone_date_after.day)
            self.assertEqual(timezone_date_orig.hour, timezone_date_after.hour)

    def test_cron(self):
        user = self.env.ref("base.user_root")
        user.write({"tz": "Europe/Paris"})
        user.invalidate_recordset()
        cron = self.env["ir.cron"].create(
            {
                "name": "TestCron",
                "model_id": self.env.ref("base.model_res_partner").id,
                "state": "code",
                "code": "model.search([])",
                "interval_number": 1,
                "interval_type": "days",
                "numbercall": -1,
                "doall": False,
            }
        )
        # from summer time to winter time
        self._check_cron_date_after_run(cron, "2021-10-30 15:00:00")
        # from winter time to summer time
        self._check_cron_date_after_run(cron, "2021-03-27 15:00:00")
