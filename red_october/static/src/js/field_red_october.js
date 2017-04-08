/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */

odoo.define('red_october.FieldRedOctober', function (require) {
    "use strict";

    var core = require('web.core');
    var common = require('web.form_common');
    var formats = require('web.formats');

    var DialogPasswordGet = require('red_october.DialogPasswordGet');

    var FieldRedOctober = common.AbstractField.extend(common.ReinitializeFieldMixin, {

        template: 'red_october.FieldRedOctober',

        SECURED: '*** SECURED ***',

        /*
            Interface Methods
         */

        init: function (field_manager, node) {
            this._super(field_manager, node);
            this.cryptCount = 0;
            this.cryptAttempted = false;
            this.clearValues();
        },

        initialize_content: function() {
            if(!this.get('effective_readonly') && !this.$input) {
                this.$input = this.$el;
            }
            this.setupFocus(this.$el);
        },

        commit_value: function () {
            var result = this._super();
            this.storeDomValue();
            var doEncrypt = $.proxy(function() {
                this.cryptDefer = $.Deferred();
                this.doEncrypt();
                return this.cryptDefer;
            }, this)
            if (this.cryptSuccess) {
                // Handle clearing values
                if (!this.valueDecrypted) {
                    this.valueEncrypted = false;
                    return result;
                }
                return doEncrypt();
            } else if (!this.cryptAttempted && !this.get('effective_readonly')) {
                return doEncrypt();
            }
            return result;
        },

        destroy_content: function() {
            this.$input = undefined;
        },

        get_value: function () {
            return this.valueDecrypted || this.valueEncrypted;
        },

        set_value: function (value, decrypted) {
            var sameRecord = this.sameRecord();
            if (!sameRecord || !value) {
                this.clearValues();
            }
            if ((!this.cryptAttempted || this.cryptSuccess) && decrypted) {
                this.valueDecrypted = value;
            } else {
                this.valueEncrypted = value;
                this.set('value', value);
                if (value && !this.valueDecrypted) {
                    this.doDecrypt();
                }
            }
        },

        render_value: function() {
            var show_value = this.format_value(this.get_value(), '');
            if (this.cryptAttempted && !this.cryptCount && show_value) {
                show_value = this.SECURED;
            }
            if (this.$input) {
                this.$input.val(show_value);
                this.$input.prop('readonly', this.isReadOnly());
            } else {
                this.$el.text(show_value);
            }
        },

        is_syntax_valid: function() {
            if (this.$input) {
                try {
                    var val = this.$input.val();
                    this.parse_value(val, '');
                    if (val === this.SECURED) {
                        return false;
                    }
                } catch(e) {
                    return false;
                }
            }
            return true;
        },

        parse_value: function(val, def) {
            return formats.parse_value(val, this, def);
        },

        format_value: function(val, def) {
            return formats.format_value(val, this, def);
        },

        is_false: function() {
            return this.get('value') === '' || this._super();
        },

        focus: function() {
            if (this.$input) {
                return this.$input.focus();
            }
            return false;
        },

        /*
            Helper Methods
         */

        clearValues: function () {
            this.valueDecrypted = false;
            this.valueEncrypted = false;
            this.cryptSuccess = false;
            this.cryptDefer = false;
            this.set('value', false);
        },

        doDecrypt: function () {
            var value = this.get_value();
            if (this.valueDecrypted && this.valueDecrypted === value) {
                return;
            }
            $('#roUserMenu').trigger(
                'decrypt',
                this
            );
        },

        doEncrypt: function () {
            var value = this.get_value();
            if (this.valueEncrypted && this.valueEncrypted === value) {
                return;
            }
            $('#roUserMenu').trigger(
                'encrypt',
                this
            );
        },

        handleCrypt: function (value, decrypted) {
            this.cryptSuccess = true;
            this.cryptAttempted = true;
            this.cryptCount += 1;
            this.set_value(value, decrypted);
            if (this.cryptDefer) {
                // This is very hacky
                var decrypted = this.valueDecrypted;
                this.valueDecrypted = false;
                this.render_value();
                debugger;
                this.cryptDefer.resolve(true);
                this.cryptDefer = false;
                this.valueDecrypted = decrypted;
            } else {
                this.render_value();
            }
        },

        storeDomValue: function () {
            if (this.$input && this.is_syntax_valid()) {
                this.set_value(
                    this.parse_value(this.$input.val()),
                    !this.cryptAttempted || this.cryptSuccess
                );
            }
        },

        isReadOnly: function () {
            return (this.get_value() && (!this.cryptSuccess ||
                                         this.get('effective_readonly') ||
                                         !this.valueDecrypted));
        },

        sameRecord: function () {
            if (this.currentId === this.view.datarecord.id) {
                return true;
            }
            this.currentId = this.view.datarecord.id;
            return false;
        }

    });

    core.form_widget_registry.add(
        'red_october', FieldRedOctober
    )

    return FieldRedOctober;

});
