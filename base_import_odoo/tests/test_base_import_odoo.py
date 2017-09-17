# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from mock import patch
from openerp.tests.common import TransactionCase, post_install, at_install


class TestBaseImportOdoo(TransactionCase):
    @at_install(False)
    @post_install(True)
    @patch('erppeek.Client.__init__', side_effect=lambda *args: None)
    def test_base_import_odoo(self, mock_client_init):
        # the mocked functions simply search/read in the current database
        # the effect then should be that the models in question are duplicated,
        # we just need to try not to be confused by the fact that local and
        # remote ids are the same
        def _mock_search(
                model, domain, offset=0, limit=None, order=None, context=None,
        ):
            return self.env[model].with_context(
                **(context or self.env.context)
            ).search(
                domain, offset=offset, limit=limit, order=order,
            ).ids

        def _mock_read(
            model, domain_or_ids, fields=None, offset=0, limit=None,
            order=None, context=None,
        ):
            return self.env[model].with_context(
                **(context or self.env.context)
            ).browse(domain_or_ids).read(fields=fields)

        for dummy in range(2):
            # we run this two times to enter the code path where xmlids exist
            self.env.ref('base_import_odoo.demodb').write({
                'password': 'admin',
            })
            with patch('erppeek.Client.search', side_effect=_mock_search):
                with patch('erppeek.Client.read', side_effect=_mock_read):
                    self.env.ref('base_import_odoo.demodb')._run_import()
            # here the actual test begins - check that we created new
            # objects, check xmlids, check values, check if dummies are
            # cleaned up/replaced
            self.assertNotEqual(
                self.env.ref(self._get_xmlid('base.user_demo')),
                self.env.ref('base.user_demo'),
            )
            self.assertEqual(
                dict(self.env.ref(self._get_xmlid('base.user_demo'))._cache),
                dict(self.env.ref('base.user_demo')._cache),
            )
            # TODO: test much more
        demodb = self.env.ref('base_import_odoo.demodb')
        demodb.action_import()
        self.assertTrue(demodb.cronjob_id)
        demodb.cronjob_id.write({'active': False})
        demodb.action_import()
        self.assertTrue(demodb.cronjob_id.active)
        self.assertFalse(demodb.cronjob_running)

    def _get_xmlid(self, remote_xmlid):
        remote_obj = self.env.ref(remote_xmlid)
        return 'base_import_odoo.%d-%s-%s' % (
            self.env.ref('base_import_odoo.demodb').id,
            remote_obj._name.replace('.', '_'),
            remote_obj.id,
        )
