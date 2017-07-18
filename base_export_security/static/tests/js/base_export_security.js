/* Copyright 2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */

odoo.define_section('base_export_security',
                    ['web.core', 'web.data', 'web.data_manager', 'web.ListView'],
                    function(test, mock) {
    'use strict';

    function setup (authorization) {
      mock.add('test.model:read', function () {
          return [{ id: 1, a: 'foo', b: 'bar', c: 'baz' }];
      });

      mock.add('res.users:has_group', function () {
          return authorization;
      });
    }

    function fields_view_get () {
        return {
            type: 'tree',
            fields: {
                a: {type: 'char', string: 'A'},
                b: {type: 'char', string: 'B'},
                c: {type: 'char', string: 'C'}
            },
            arch: '<tree><field name="a"/><field name="b"/><field name="c"/></tree>'
        };
    }

    function labelCount (exportLabel) {
        var $fix = $('#qunit-fixture');
        var exportItems = $fix.find('.btn-group a[data-section="other"]').filter(
            function(i, item){
                return item.text.trim() === exportLabel;
            }
        );

        return exportItems.length;
    }

    function renderView (data, data_manager, ListView) {
        var $fix = $('#qunit-fixture');
        var dataset = new data.DataSetStatic(null, 'test.model', null, [1]);
        var fields_view = data_manager._postprocess_fvg(fields_view_get());
        var listView = new ListView({}, dataset, fields_view, {sidebar: true});

        listView.appendTo($fix)
        .then(listView.render_sidebar($fix));
    }

    test('It should display the Export menu item to authorized users',
        function(assert, core, data, data_manager, ListView) {
            var exportLabel = core._t('Export');
            setup(true);
            renderView(data, data_manager, ListView);

            assert.strictEqual(labelCount(exportLabel), 1);
        }
    );

    test('It should not display the Export menu item to unauthorized users',
        function(assert, core, data, data_manager, ListView) {
            var exportLabel = core._t('Export');
            setup(false);
            renderView(data, data_manager, ListView);

            assert.strictEqual(labelCount(exportLabel), 0);
        }
    );

});
