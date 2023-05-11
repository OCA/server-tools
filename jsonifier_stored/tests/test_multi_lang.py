# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from .common import (
    RecordCapturer,
    TestJsonifyStoredCase,
    perform_jobs,
    setup_multi_lang_data,
)


class TestMultiLang(TestJsonifyStoredCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setup_multi_lang_data(cls)

    def test_json_data(self):
        self.assertEqual(
            self.all_records_multilang.mapped("jsonified_data"),
            [{}] * len(self.all_records_multilang),
        )
        self.all_records_multilang._compute_jsonified_data()
        for lang in self.all_langs:
            records = self.all_records_multilang.filtered(lambda x: x.lang_id == lang)
            for data, expected in zip(
                records.mapped("jsonified_data"), self.expected_multilang[lang.code]
            ):
                self.assertEqual(data, expected)

    def test_jobify(self):
        with RecordCapturer(self.env["queue.job"], []) as capt:
            self.jstored_mixin_model.jobify_json_data_compute_for(
                self.fake_model_multilang
            )
            jobs = capt.records
            # chunk size == 5, we have 15 records
            self.assertEqual(len(jobs), 3)
            self.assertEqual(
                jobs[0].name,
                f"Compute JSON data for: {self.fake_model_multilang._name}",
            )
            perform_jobs(jobs)

        for lang in self.all_langs:
            records = self.all_records_multilang.filtered(lambda x: x.lang_id == lang)
            for data, expected in zip(
                records.mapped("jsonified_data"), self.expected_multilang[lang.code]
            ):
                self.assertEqual(data, expected)

        # set chunk size to 1
        with RecordCapturer(self.env["queue.job"], []) as capt:
            self.jstored_mixin_model.jobify_json_data_compute_for(
                self.fake_model_multilang, chunk_size=1
            )
            jobs = capt.records
            self.assertEqual(len(jobs), len(self.all_records_multilang))
