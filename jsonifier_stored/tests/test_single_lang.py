# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import (
    RecordCapturer,
    TestJsonifyStoredCase,
    perform_jobs,
    setup_single_lang_data,
)


class TestNoLang(TestJsonifyStoredCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setup_single_lang_data(cls)

    def test_json_data(self):
        self.assertEqual(
            self.all_records.mapped("jsonified_data"), [{}] * len(self.all_records)
        )
        self.all_records._compute_jsonified_data()
        for data, expected in zip(
            self.all_records.mapped("jsonified_data"), self.expected
        ):
            self.assertEqual(data, expected)

    def test_jobify(self):
        with RecordCapturer(self.env["queue.job"], []) as capt:
            self.jstored_mixin_model.jobify_json_data_compute_for(self.fake_model)
            jobs = capt.records
            # chunk size == 5
            self.assertEqual(len(jobs), 1)
            self.assertEqual(
                jobs.name, f"Compute JSON data for: {self.fake_model._name}"
            )
            perform_jobs(jobs)
        for data, expected in zip(
            self.all_records.mapped("jsonified_data"), self.expected
        ):
            self.assertEqual(data, expected)

        # set chunk size to 1
        with RecordCapturer(self.env["queue.job"], []) as capt:
            self.jstored_mixin_model.jobify_json_data_compute_for(
                self.fake_model, chunk_size=1
            )
            jobs = capt.records
            self.assertEqual(len(jobs), len(self.all_records))
