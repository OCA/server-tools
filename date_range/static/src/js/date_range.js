/* © 2016 ACSONE SA/NV (<http://acsone.eu>)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
odoo.define('date_range.search_filters', function (require) {
"use strict";

var core = require('web.core'); 
var datepicker = require('web.datepicker');
var formats = require('web.formats');
var Widget = require('web.Widget');

var data = require('web.data');
var filters = require('web.search_filters');
var Model = require('web.Model');
var framework = require('web.framework');

var _t = core._t;
var _lt = core._lt;
filters.ExtendedSearchProposition.include({
    select_field: function(field) {
        this._super.apply(this, arguments);
        this.is_date = field.type == 'date' || field.type == 'datetime';
        this.$value = this.$('.searchview_extended_prop_value');
        if (this.is_date){
            var ds = new data.DataSetSearch(this, 'date.range.type', this.context, [[1, '=', 1]]);
            ds.read_slice(['name'], {}).done(this.proxy('add_date_range_types_operator'));
        }
    },
    
    add_date_range_types_operator: function(date_range_types){
        var self = this;
        _.each(date_range_types, function(drt) {
            $('<option>', {value: 'drt_' + drt.id})
                .text(drt.name)
                .appendTo(self.$('.searchview_extended_prop_op'));
        });
    },
    
    operator_changed: function (e) {
        var val = $(e.target).val();
        if (val.startsWith('drt_')){
            var type_id = val.replace('drt_', '');
            this.date_range_type_operator_selected(type_id);
            return;
        }
        this._super.apply(this, arguments);
    },

    date_range_type_operator_selected: function(type_id){
        this.$value.show().empty();
        var ds = new data.DataSetSearch(this, 'date.range', this.context, [['type_id', '=', parseInt(type_id)]]);
        ds.read_slice(['name','date_start', 'date_end'], {}).done(this.proxy('on_range_type_selected'));
            
    },
    
    on_range_type_selected: function(date_range_values){
        this.value = new filters.ExtendedSearchProposition.DateRange(this, this.value.field, date_range_values);
        this.value.appendTo(this.$value);
    },
    
});

filters.ExtendedSearchProposition.DateRange = filters.ExtendedSearchProposition.Field.extend({
    template: 'SearchView.extended_search.dateRange.selection',
    events: {
        'change .date-range-select': 'on_range_selected',
    },
    
    init: function (parent, field, date_range_values) {
        this._super(parent, field);
        this.date_range_values = date_range_values;
    },

    toString: function () {
        var select = this.$el[0];
        var option = select.options[select.selectedIndex];
        return option.label || option.text;
    },
    
    get_value: function() {
        return parseInt(this.$el.val());
    },

     renderElement: function() {
        this._super();
        var self = this;
        this.$el.find('.date-range-select').on('change', function(){
            self.on_range_selected();
        });
    },
    
    on_range_selected: function(e){
        var self = this;
        self.domain = '';
        framework.blockUI();
        new Model("date.range")
                .call("get_domain",  [
                [this.get_value()],
                 this.field.name,
                 {}
         ])
        .then(function (domain) {
            framework.unblockUI();
            self.domain = JSON.stringify(domain);
        });
    },
    
    get_domain: function (field, operator) {
        return this.domain;
    },
});

});