# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <http://therp.nl>
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from mock import Mock, patch
import os
import tempfile
from openerp.modules.module import load_information_from_description_file,\
    get_module_path, MANIFEST
from openerp.tests.common import TransactionCase
from ..hooks import _handle_rdepends_if_installed, _installed_modules

MOCK_PATH = 'openerp.addons.base_manifest_extension.hooks'


class TestHooks(TransactionCase):
    def setUp(self):
        super(TestHooks, self).setUp()

        self.test_cr = self.env.cr
        self.test_rdepends = [
            'base',
            'base_manifest_extension',
            'not_installed',
        ]
        self.test_manifest = {
            'rdepends_if_installed': self.test_rdepends,
            'depends': [],
        }
        self.test_module_name = 'base_manifest_extension'
        self.test_call = (
            self.test_cr,
            self.test_manifest,
            self.test_module_name,
        )

    def test_base_manifest_extension(self):
        # write a test manifest
        module_path = tempfile.mkdtemp(dir=os.path.join(
            get_module_path('base_manifest_extension'), 'static'
        ))
        with open(os.path.join(module_path, MANIFEST), 'w') as manifest:
            manifest.write(repr({
                'depends_if_installed': [
                    'base_manifest_extension',
                    'not installed',
                ],
            }))
        # parse it
        parsed = load_information_from_description_file(
            # this name won't really be used, but avoids a warning
            'base', mod_path=module_path,
        )
        self.assertIn('base_manifest_extension', parsed['depends'])
        self.assertNotIn('not installed', parsed['depends'])
        self.assertNotIn('depends_if_installed', parsed)

    def test_installed_modules_correct_result(self):
        """It should return only installed modules in list"""
        result = _installed_modules(self.test_cr, self.test_rdepends)

        expected = self.test_rdepends[:2]
        self.assertItemsEqual(result, expected)

    def test_installed_modules_empty_starting_list(self):
        """It should safely handle being passed an empty module list"""
        result = _installed_modules(self.test_cr, [])

        self.assertEqual(result, [])

    @patch(MOCK_PATH + '._get_graph')
    def test_handle_rdepends_if_installed_graph_call(self, graph_mock):
        """It should call graph helper and return early if graph not found"""
        graph_mock.return_value = None
        graph_mock.reset_mock()
        self.test_cr = Mock()
        self.test_cr.reset_mock()
        _handle_rdepends_if_installed(*self.test_call)

        graph_mock.assert_called_once()
        self.test_cr.assert_not_called()

    @patch(MOCK_PATH + '._get_graph')
    def test_handle_rdepends_if_installed_clean_manifest(self, graph_mock):
        """It should remove rdepends key from manifest"""
        _handle_rdepends_if_installed(*self.test_call)

        self.assertEqual(self.test_manifest, {'depends': []})

    @patch(MOCK_PATH + '.local.rdepends_to_process', new_callable=dict)
    @patch(MOCK_PATH + '._get_graph')
    def test_handle_rdepends_if_installed_list(self, graph_mock, dict_mock):
        """It should correctly add all installed rdepends to processing dict"""
        _handle_rdepends_if_installed(*self.test_call)

        expected_result = {
            'base': set([self.test_module_name]),
            'base_manifest_extension': set([self.test_module_name]),
        }
        self.assertEqual(dict_mock, expected_result)

    @patch(MOCK_PATH + '.local.rdepends_to_process', new_callable=dict)
    @patch(MOCK_PATH + '._get_graph')
    def test_handle_rdepends_if_installed_dupes(self, graph_mock, dict_mock):
        """It should correctly handle multiple calls with same rdepends"""
        for __ in range(2):
            _handle_rdepends_if_installed(*self.test_call)
            self.test_manifest['rdepends_if_installed'] = self.test_rdepends
        test_module_name_2 = 'test_module_name_2'
        _handle_rdepends_if_installed(
            self.test_cr,
            self.test_manifest,
            test_module_name_2,
        )

        expected_set = set([self.test_module_name, test_module_name_2])
        expected_result = {
            'base': expected_set,
            'base_manifest_extension': expected_set,
        }
        self.assertEqual(dict_mock, expected_result)

    @patch(MOCK_PATH + '._get_graph')
    def test_handle_rdepends_if_installed_graph_reload(self, graph_mock):
        """It should reload installed rdepends already in module graph"""
        class TestGraph(dict):
            pass

        test_graph = TestGraph(base='Test Value')
        test_graph.add_module = Mock()
        graph_mock.return_value = test_graph
        _handle_rdepends_if_installed(*self.test_call)

        self.assertEqual(test_graph, {})
        test_graph.add_module.assert_called_once_with(self.cr, 'base')

    @patch(MOCK_PATH + '._handle_rdepends_if_installed')
    @patch(MOCK_PATH + '._get_cr')
    @patch(MOCK_PATH + '.original')
    def test_load_information_from_description_file_rdepends_key(
        self, super_mock, cr_mock, helper_mock
    ):
        """It should correctly call rdepends helper if key present"""
        super_mock.return_value = self.test_manifest
        cr_mock.return_value = self.cr
        helper_mock.reset_mock()
        load_information_from_description_file(self.test_module_name)

        helper_mock.assert_called_once_with(*self.test_call)

    @patch(MOCK_PATH + '._handle_rdepends_if_installed')
    @patch(MOCK_PATH + '._get_cr')
    @patch(MOCK_PATH + '.original')
    def test_load_information_from_description_file_no_rdepends_key(
        self, super_mock, cr_mock, helper_mock
    ):
        """It should not call rdepends helper if key not present"""
        del self.test_manifest['rdepends_if_installed']
        super_mock.return_value = self.test_manifest
        cr_mock.return_value = self.cr
        helper_mock.reset_mock()
        load_information_from_description_file(self.test_module_name)

        helper_mock.assert_not_called()

    @patch(MOCK_PATH + '._get_cr')
    @patch(MOCK_PATH + '.original')
    def test_load_information_from_description_file_rdepends_to_process(
        self, super_mock, cr_mock
    ):
        """It should correctly add pending rdepends to manifest"""
        del self.test_manifest['rdepends_if_installed']
        super_mock.return_value = self.test_manifest
        cr_mock.return_value = self.cr
        test_depends = set(['Test Depend 1', 'Test Depend 2'])
        test_rdepend_dict = {
            self.test_module_name: test_depends,
            'Other Module': set(['Other Depend']),
        }
        dict_path = MOCK_PATH + '.local.rdepends_to_process'
        with patch.dict(dict_path, test_rdepend_dict, clear=True):
            load_information_from_description_file(self.test_module_name)

        self.assertEqual(self.test_manifest['depends'], list(test_depends))
