# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import (
    RecordCapturer,
    TestJsonifyStoredCase,
    perform_jobs,
    setup_multi_lang_data,
    setup_single_lang_data,
)


class TestNoLang(TestJsonifyStoredCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setup_single_lang_data(cls)
        setup_multi_lang_data(cls)

    def test_cron(self):
        with RecordCapturer(self.env["queue.job"], []) as capt:
            self.cron.method_direct_trigger()
            jobs = capt.records
            # chunk size == 5
            self.assertEqual(
                len(jobs), (len(self.all_records) + len(self.all_records_multilang)) / 5
            )
            self.assertEqual(
                sorted(jobs.mapped("name")),
                sorted(
                    [
                        f"Compute JSON data for: {self.fake_model._name}",
                        f"Compute JSON data for: {self.fake_model_multilang._name} (en_US)",
                        f"Compute JSON data for: {self.fake_model_multilang._name} (fr_FR)",
                        f"Compute JSON data for: {self.fake_model_multilang._name} (de_DE)",
                    ]
                ),
            )
            perform_jobs(jobs)

        for data, expected in zip(
            self.all_records.mapped("jsonified_data"), self.expected
        ):
            self.assertEqual(data, expected)

        for lang in self.all_langs:
            records = self.all_records_multilang.filtered(lambda x: x.lang_id == lang)
            for data, expected in zip(
                records.mapped("jsonified_data"), self.expected_multilang[lang.code]
            ):
                self.assertEqual(data, expected)

    def test_cron_chunk_size(self):
        model = self.jstored_mixin_model
        with RecordCapturer(self.env["queue.job"], []) as capt:
            for child_model in model._inherit_children:
                model.cron_update_json_data_for(child_model, chunk_size=2)
            jobs = capt.records
            self.assertEqual(len(jobs), 12)
            self.assertEqual(
                sorted(jobs.mapped("name")),
                sorted(
                    [
                        f"Compute JSON data for: {self.fake_model._name}",
                        f"Compute JSON data for: {self.fake_model._name}",
                        f"Compute JSON data for: {self.fake_model._name}",
                        f"Compute JSON data for: {self.fake_model_multilang._name} (en_US)",
                        f"Compute JSON data for: {self.fake_model_multilang._name} (en_US)",
                        f"Compute JSON data for: {self.fake_model_multilang._name} (en_US)",
                        f"Compute JSON data for: {self.fake_model_multilang._name} (fr_FR)",
                        f"Compute JSON data for: {self.fake_model_multilang._name} (fr_FR)",
                        f"Compute JSON data for: {self.fake_model_multilang._name} (fr_FR)",
                        f"Compute JSON data for: {self.fake_model_multilang._name} (de_DE)",
                        f"Compute JSON data for: {self.fake_model_multilang._name} (de_DE)",
                        f"Compute JSON data for: {self.fake_model_multilang._name} (de_DE)",
                    ]
                ),
            )
