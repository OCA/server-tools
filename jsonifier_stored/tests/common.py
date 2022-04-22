# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo_test_helper import FakeModelLoader

from odoo import tools
from odoo.modules.module import get_resource_path
from odoo.tests.common import SavepointCase

from odoo.addons.queue_job.job import Job


def load_xml(env, module, filepath):
    tools.convert_file(
        env.cr,
        module,
        get_resource_path(module, filepath),
        {},
        mode="init",
        noupdate=False,
        kind="test",
    )


# TODO: move to queue_job
def perform_jobs(jobs):
    for job in jobs:
        Job.load(jobs.env, job.uuid).perform()


class TestCaseBase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,  # speed up tests
            )
        )

    @classmethod
    def _load_fixture(cls, fixture, module="jsonifier_stored"):
        load_xml(cls.env, module, "tests/fixtures/%s" % fixture)


class TestJsonifyStoredCase(TestCaseBase, FakeModelLoader):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Load fake models ->/
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .fake_models import FakeTestModel, FakeTestModelMultiLang

        cls.loader.update_registry((FakeTestModel, FakeTestModelMultiLang))
        cls.jstored_mixin_model = cls.env["jsonifier.stored.mixin"]
        cls.fake_model = cls.env[FakeTestModel._name]
        cls.fake_model_multilang = cls.env[FakeTestModelMultiLang._name]
        # ->/ Load fake models
        cls._load_fixture("ir_exports_test.xml")
        cls.cron = cls.env.ref("jsonifier_stored.cron_recompute_all")

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()


def setup_single_lang_data(cls):
    cls.expected = []
    cls.all_records = cls.fake_model.browse()
    for x in range(1, 6):
        vals = {
            "name": f"Fake {x}",
            "description": f"Fake descr {x}",
        }
        rec = cls.fake_model.create(vals)
        cls.all_records += rec
        setattr(cls, f"rec_{x}", rec)
        cls.expected.append(dict(vals, id=rec.id))


def setup_multi_lang_data(cls):
    cls.lang_en = cls.env.ref("base.lang_en")
    cls.lang_fr = cls.env.ref("base.lang_fr")
    cls.lang_de = cls.env.ref("base.lang_de")
    cls.lang_fr.active = True
    cls.lang_de.active = True
    cls.expected_multilang = defaultdict(list)
    cls.all_records_multilang = cls.fake_model_multilang.browse()
    cls.title = cls.env["res.partner.title"].create({"name": "Title"})
    cls.title.with_context(lang="fr_FR").name = "Title FR"
    cls.title.with_context(lang="de_DE").name = "Title DE"
    cls.all_langs = (cls.lang_en, cls.lang_fr, cls.lang_de)
    for lang in cls.all_langs:
        for x in range(1, 6):
            vals = {
                "name": f"Fake {x} [{lang.code}]",
                "description": f"Fake descr {x}",
                "lang_id": lang.id,
                "title_id": cls.title.id,
            }
            rec = cls.fake_model_multilang.create(vals)
            cls.all_records_multilang += rec
            setattr(cls, f"rec_{lang.code}_{x}", rec)
            expected = dict(vals, id=rec.id)
            expected.pop("lang_id")
            expected.pop("title_id")
            expected["title"] = cls.title.with_context(lang=lang.code).name
            cls.expected_multilang[lang.code].append(expected)


# This will be available in V15 and we should replace `queue_job.tests.JobCounter`
class RecordCapturer:
    def __init__(self, model, domain):
        self._model = model
        self._domain = domain

    def __enter__(self):
        self._before = self._model.search(self._domain)
        self._after = None
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is None:
            self._after = self._model.search(self._domain) - self._before

    @property
    def records(self):
        if self._after is None:
            return self._model.search(self._domain) - self._before
        return self._after
