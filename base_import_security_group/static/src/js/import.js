odoo.define('web.ListImport', function (require) {
    "use strict";

    // Backport from v13:
    // https://github.com/odoo/odoo/commit/55676110c8787dfafd34a6508b207952f5c5eb88

    var config = require('web.config');
    var ListView = require('web.ListView');
    var KanbanView = require('web.KanbanView');


    var ImportViewMixin = {
        /**
         * @override
         * @param {Object} params
         * @param {boolean} [params.import_enabled=true] set to false to disable
         *   the Import feature (no 'Import' button in the control panel). Can also
         *   be disabled with 'import' attrs set to '0' in the arch.
         */
        init: function (viewInfo, params) {
            var importEnabled = !!JSON.parse(this.arch.attrs.import || '1') &&
                ('import_enabled' in params ? params.import_enabled : true);
            this.controllerParams.importEnabled = importEnabled && !config.device.isMobile;
        },
    };

    ListView.include({
        init: function () {
            this._super.apply(this, arguments);
            ImportViewMixin.init.apply(this, arguments);
        },
    });

    KanbanView.include({
        init: function () {
            this._super.apply(this, arguments);
            ImportViewMixin.init.apply(this, arguments);
        },
    });

});
