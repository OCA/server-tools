# Copyright 2020 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import shutil

from odoo.tests import HttpCase
from odoo.tools.misc import mute_logger

from ..models.letsencrypt import _get_challenge_dir


class TestHTTP(HttpCase):
    def test_query_existing(self):
        with open(os.path.join(_get_challenge_dir(), "foobar"), "w") as file:
            file.write("content")
        res = self.url_open("/.well-known/acme-challenge/foobar")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, "content")

    @mute_logger("odoo.addons.letsencrypt.controllers.main")
    def test_query_missing(self):
        res = self.url_open("/.well-known/acme-challenge/foobar")
        self.assertEqual(res.status_code, 404)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(_get_challenge_dir(), ignore_errors=True)
