# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestLetsencrypt(TransactionCase):
    def test_letsencrypt(self):
        from ..hooks import post_init_hook
        post_init_hook(self.cr, None)
        self.env.ref('letsencrypt.config_parameter_reload').write({
            'value': '',
        })
        self.env['letsencrypt'].with_context(letsencrypt_dry_run=True).cron()
