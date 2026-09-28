# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from unittest.mock import patch

import fsspec

from odoo.tests import TransactionCase
from odoo.tools import mute_logger

LOG_MODEL = "odoo.addons.data_import_log.models.data_import_log.DataImportLog"
FEED = b"key,qty\nD-1,2\nD-2,3\n"


class TestDataImportPickup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
        cls.backend = cls.env["fs.storage"].create(
            {
                "name": "Test Memory",
                "code": "test_memory",
                "protocol": "memory",
                "directory_path": "/test_pickup",
            }
        )
        cls.pickup = cls.env["data.import.pickup"].create(
            {"name": "Test Feed", "backend_id": cls.backend.id}
        )

    def setUp(self):
        super().setUp()
        # The memory filesystem is process-wide, so each test starts it empty.
        memory = fsspec.filesystem("memory")
        if memory.exists("/test_pickup"):
            memory.rm("/test_pickup", recursive=True)
        for path in ("in", "processing", "done", "error"):
            memory.makedirs(f"/test_pickup/{path}", exist_ok=True)
        self.fs = self.pickup.backend_id.fs

    def _put(self, name, content=FEED):
        with self.fs.open(f"in/{name}", "wb") as fh:
            fh.write(content)

    def _names(self, path):
        return sorted(p.rsplit("/", 1)[-1] for p in self.fs.ls(path, detail=False))

    def test_file_is_taken_in_and_held(self):
        self._put("feed.csv")
        with patch(f"{LOG_MODEL}._import_unit", return_value=[]):
            logs = self.pickup._scan()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.file_name, "feed.csv")
        self.assertEqual(logs.state, "done")
        self.assertEqual(logs.unit_total, 2)
        self.assertEqual(self._names("in"), [])
        self.assertEqual(self._names("done"), ["feed.csv"])
        self.assertEqual(self._names("processing"), [])

    def test_column_names_of_the_pickup_reach_the_log(self):
        # The header says something else: the columns are read by position.
        self.pickup.column_names = "doc\nqty"
        self._put("feed.csv", b"A,B\nD-1,2\n")
        with patch(f"{LOG_MODEL}._import_unit", return_value=[]):
            logs = self.pickup._scan()
        self.assertEqual(logs.column_names, "doc\nqty")
        self.assertEqual(
            logs._read_rows(), (["doc", "qty"], [{"doc": "D-1", "qty": "2"}])
        )
        self.pickup.column_names = False

    def test_file_still_being_imported_is_not_overwritten(self):
        self._put("feed.csv")
        # The first import is still in flight: its units were never run.
        with patch(f"{LOG_MODEL}._enqueue_unit"):
            first = self.pickup._scan()
        self.assertEqual(first.state, "processing")
        # The sender resends the same name with corrected content.
        self._put("feed.csv", b"key,qty\nD-9,9\n")
        second = self.pickup._scan()
        self.assertFalse(second)
        # The held copy is untouched and the new one waits its turn.
        with self.fs.open("processing/feed.csv", "rb") as fh:
            self.assertEqual(fh.read(), FEED)
        self.assertEqual(self._names("in"), ["feed.csv"])

    def test_pickups_are_scanned_in_sequence(self):
        # A feed whose files depend on one another needs the pick-ups scanned
        # in a known order, not in the order they were created.
        second = self.pickup.copy({"name": "Second Feed", "sequence": 1})
        scanned = []
        with patch(
            "odoo.addons.data_import_log_fs.models.data_import_pickup"
            ".DataImportPickup._scan_one",
            lambda self, logs: scanned.append(self.name) or logs,
        ):
            (self.pickup | second)._scan()
        self.assertEqual(scanned, ["Second Feed", self.pickup.name])

    def test_incomplete_file_is_left_alone(self):
        self._put("feed.csv.tmp")
        logs = self.pickup._scan()
        self.assertFalse(logs)
        self.assertEqual(self._names("in"), ["feed.csv.tmp"])

    def test_unmatched_name_is_left_alone(self):
        self._put("notes.txt")
        logs = self.pickup._scan()
        self.assertFalse(logs)
        self.assertEqual(self._names("in"), ["notes.txt"])

    def test_file_imported_in_full_is_not_taken_again(self):
        self._put("feed.csv")
        with patch(f"{LOG_MODEL}._import_unit", return_value=[]):
            self.pickup._scan()
            self._put("feed.csv")
            logs = self.pickup._scan()
        self.assertFalse(logs)
        self.assertEqual(self._names("in"), ["feed.csv"])
        self.assertEqual(
            self.env["data.import.log"].search_count([("file_name", "=", "feed.csv")]),
            1,
        )

    def test_resent_file_is_taken_again_after_a_rejection(self):
        # The sender corrects a rejected unit by sending the same file again.
        self._put("feed.csv")
        errors = [{"error_message": "no matching order"}]
        with patch(f"{LOG_MODEL}._import_unit", return_value=errors):
            first = self.pickup._scan()
        self.assertEqual(first.state, "error")
        self._put("feed.csv")
        with patch(f"{LOG_MODEL}._import_unit", return_value=[]):
            second = self.pickup._scan()
        self.assertEqual(len(second), 1)
        self.assertEqual(second.state, "done")

    def test_same_name_new_content_is_taken_in(self):
        self._put("feed.csv")
        with patch(f"{LOG_MODEL}._import_unit", return_value=[]):
            self.pickup._scan()
            self._put("feed.csv", b"key,qty\nD-9,9\n")
            logs = self.pickup._scan()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.unit_total, 1)

    def test_rejected_units_still_release_the_file(self):
        self._put("feed.csv")
        errors = [{"error_message": "no matching order"}]
        with patch(f"{LOG_MODEL}._import_unit", return_value=errors):
            logs = self.pickup._scan()
        self.assertEqual(logs.state, "error")
        self.assertEqual(self._names("done"), ["feed.csv"])

    def test_file_is_held_while_units_are_in_flight(self):
        self._put("feed.csv")
        with patch(f"{LOG_MODEL}._enqueue_unit"):
            logs = self.pickup._scan()
        self.assertEqual(logs.state, "processing")
        self.assertEqual(self._names("processing"), ["feed.csv"])
        self.assertEqual(self._names("done"), [])

    def test_several_files_are_taken_in_name_order(self):
        # Order is by name, not by what the directory happens to list first, so
        # that a feed numbering its files is imported in sequence.
        self._put("b.csv")
        self._put("a.csv")
        with patch(f"{LOG_MODEL}._import_unit", return_value=[]):
            logs = self.pickup._scan()
        self.assertEqual(logs.mapped("file_name"), ["a.csv", "b.csv"])
        self.assertEqual(self._names("done"), ["a.csv", "b.csv"])

    def test_missing_incoming_directory_is_not_an_error(self):
        self.fs.rm("in", recursive=True)
        self.assertFalse(self.pickup._scan())

    @mute_logger("odoo.addons.data_import_log.models.data_import_log")
    def test_unreadable_file_is_isolated_whole(self):
        # Latin-1 content read as UTF-8: the file itself cannot be read.
        self._put("feed.csv", "réf,qty\nD-1,2\n".encode("iso-8859-1"))
        logs = self.pickup._scan()
        self.assertTrue(logs.file_error)
        self.assertEqual(logs.state, "error")
        self.assertEqual(self._names("error"), ["feed.csv"])
        self.assertEqual(self._names("done"), [])
        self.assertEqual(self._names("processing"), [])

    def test_rejected_units_are_written_to_the_error_directory(self):
        self._put("feed.csv")
        errors = [{"error_message": "no matching order"}]

        def only_second(self, unit_key, rows):
            return errors if unit_key == "2" else []

        with patch(f"{LOG_MODEL}._import_unit", only_second):
            logs = self.pickup._scan()
        self.assertEqual(logs.state, "partial")
        # The source was received whole, so it is filed as done ...
        self.assertEqual(self._names("done"), ["feed.csv"])
        # ... and only the rejected unit goes back for the sender to resend.
        self.assertEqual(self._names("error"), ["feed.csv"])
        with self.fs.open("error/feed.csv", "rb") as fh:
            self.assertEqual(fh.read(), b"key,qty\r\nD-2,3\r\n")

    def test_no_error_file_when_everything_imports(self):
        self._put("feed.csv")
        with patch(f"{LOG_MODEL}._import_unit", return_value=[]):
            self.pickup._scan()
        self.assertEqual(self._names("error"), [])

    @mute_logger("odoo.addons.data_import_log_fs.models.data_import_pickup")
    def test_one_broken_pickup_does_not_stop_the_others(self):
        # A backend that cannot be reached: no host for the sftp protocol.
        broken_backend = self.env["fs.storage"].create(
            {"name": "Broken", "code": "broken_test", "protocol": "sftp"}
        )
        broken = self.env["data.import.pickup"].create(
            {"name": "Broken Feed", "backend_id": broken_backend.id}
        )
        self._put("feed.csv")
        with patch(f"{LOG_MODEL}._import_unit", return_value=[]):
            logs = (broken | self.pickup)._scan()
        self.assertEqual(logs.file_name, "feed.csv")
        self.assertEqual(self._names("done"), ["feed.csv"])
