// Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
// License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).
odoo.define('excel_import_export.report', function(require){
'use strict';

var ActionManager= require('web.ActionManager');
var crash_manager = require('web.crash_manager');
var framework = require('web.framework');

ActionManager.include({
    ir_actions_report: function (action, options){
        var self = this;
        var cloned_action = _.clone(action);
        if (cloned_action.report_type === 'excel') {
            framework.blockUI();
            var report_excel_url = 'report/excel/' + cloned_action.report_name;
            if (_.isUndefined(cloned_action.data) ||
                _.isNull(cloned_action.data) ||
                (_.isObject(cloned_action.data) && _.isEmpty(cloned_action.data)))
            {
                if(cloned_action.context.active_ids) {
                    report_excel_url += '/' + cloned_action.context.active_ids.join(',');
                }
            } else {
                report_excel_url += '?options=' + encodeURIComponent(JSON.stringify(cloned_action.data));
                report_excel_url += '&context=' + encodeURIComponent(JSON.stringify(cloned_action.context));
            }
            self.getSession().get_file({
                url: report_excel_url,
                data: {data: JSON.stringify([
                    report_excel_url,
                    cloned_action.report_type
                ])},
                error: crash_manager.rpc_error.bind(crash_manager),
                success: function (){
                    if(cloned_action && options && !cloned_action.dialog){
                        options.on_close();
                    }
                }
            });
            framework.unblockUI();
            return;
        }
        return self._super(action, options);
    }
});
});
