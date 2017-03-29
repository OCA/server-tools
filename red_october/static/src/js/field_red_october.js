/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */

odoo.define('red_october.FieldRedOctober', function (require) {
    "use strict";

    var core = require('web.core');
    var common = require('web.form_common');

    var FieldRedOctober = common.AbstractField.extend(common.ReinitializeFieldMixin, {
        template: 'FieldRedOctober',
        events: {
            'keyup': function (e) {
                if (e.which === $.ui.keyCode.ENTER) {
                    e.stopPropagation();
                }
            },
            'keypress': function (e) {
                if (e.which === $.ui.keyCode.ENTER) {
                    e.stopPropagation();
                }
            },
            'change': 'store_dom_value',
        },
        initialize_content: function() {
            if (!this.get("effective_readonly")) {
                this.auto_sized = false;
                this.setupFocus(this.$el);
            }
        },
        commit_value: function () {
            if (!this.get("effective_readonly")) {
                this.store_dom_value();
            }
            return this._super();
        },
        store_dom_value: function () {
            this.internal_set_value(formats.parse_value(this.$el.val(), this));
        },
        render_value: function() {
            if (this.get("effective_readonly")) {
                var txt = this.get("value") || '';
                this.$el.text(txt);
            } else {
                var show_value = formats.format_value(this.get('value'), this, '');
                this.$el.val(show_value);
                dom_utils.autoresize(this.$el, {parent: this});
            }
        },
        is_syntax_valid: function() {
            if (!this.get("effective_readonly")) {
                try {
                    formats.parse_value(this.$el.val(), this, '');
                } catch(e) {
                    return false;
                }
            }
            return true;
        },
        is_false: function() {
            return this.get('value') === '' || this._super();
        },
        focus: function($el) {
            if(!this.get("effective_readonly")) {
                return this.$el.focus();
            }
            return false;
        },
        set_dimensions: function(height, width) {
            this.$el.css({
                width: width,
                minHeight: height,
            });
        },
    });

    core.form_widget_registry.add(
        'red_october', FieldRedOctober
    )

    return FieldRedOctober;

});
