odoo.define('web.ListImport', function (require) {
    "use strict";

    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var session = require('web.session');

    var ImportViewMixin = {

    init: function (viewInfo, params) {

        var self = this
        var result = self._super.apply(self, arguments);
        var base_group = 'base_import_security_group.group_import_csv';

        session.user_has_group(base_group).then(function (result){
            var importEnabled = false
            if (result){
                importEnabled =  true;
            }
            self.controllerParams.importEnabled = importEnabled;
            });
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
