# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase, at_install, post_install


@at_install(False)
@post_install(True)
class TestProfilingUI(HttpCase):
    def test_profile_creation_by_request(self):
        """We are testing the creation of a user session profile."""
        self.phantom_js(
            "/web",
            "odoo.__DEBUG__.services['web_tour.tour'].run('profiler_tour')",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.profiler_tour.ready",
            login="admin",
        )
