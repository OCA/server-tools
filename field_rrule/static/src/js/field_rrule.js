//-*- coding: utf-8 -*-
//© 2016 Therp BV <http://therp.nl>
//License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

openerp.field_rrule = function(instance)
{
    instance.field_rrule.FieldRRule = instance.web.form.AbstractField
    .extend(instance.web.form.ReinitializeFieldMixin, {
        template: 'FieldRRule',
        events: {
            'click a.add_rule': 'add_rule',
            'click a.rule_remove': 'remove_rule',
            'change select': 'frequency_changed',
            'change input:not(.rule_ignore_input)': 'input_changed',
            'change input[name="recurrence_type"]': 'toggle_recurrence_type',
        },
        set_value: function(val)
        {
            var result = this._super(jQuery.extend([], val));
            _.each(this.get('value'), function(rule)
            {
                rule['__id'] = _.uniqueId();
            });
            this.reinitialize();
            return result;
        },
        get_value: function()
        {
            var result = jQuery.extend(
                true, [], this._super.apply(this, arguments));
            _.each(result, function(rule)
            {
                delete rule['__id'];
            });
            return result;
        },
        initialize_content: function()
        {
            var self = this;
            this.$('select[name="freq"]').trigger('change', true);
            this.$('input[name="recurrence_type"]:checked')
            .trigger('change', true);
            this.$('input[type="datetime"]').each(function()
            {
                var input = jQuery(this),
                    current_value = input.val();
                input.datetimepicker({
                    closeOnDateSelect: true,
                    value: current_value ? instance.web.str_to_datetime(
                        instance.web.parse_value(
                            input.val(), {type: 'datetime'})) : new Date(),
                    dateFormat: self.datetimepicker_format(
                        instance.web._t.database.parameters.date_format),
                    timeFormat: self.datetimepicker_format(
                        instance.web._t.database.parameters.time_format),
                    changeMonth: true,
                    changeYear: true,
                    showWeek: true,
                    showButtonPanel: true,
                    firstDay: Date.CultureInfo.firstDayOfWeek,
                });
            });
        },
        datetimepicker_format: function(odoo_format)
        {
            var result = '',
                map = {
                    '%a': 'D',
                    '%A': 'DD',
                    '%b': 'M',
                    '%B': 'MM',
                    '%c': '', // locale's datetime representation
                    '%d': 'dd',
                    '%H': 'hh',
                    '%T': 'hh:mm:ss',
                    '%I': 'h',
                    '%j': '', // day of the year unsuported
                    '%m': 'm',
                    '%M': 'mm',
                    '%p': 't',
                    '%S': 'ss',
                    '%U': '', // weeknumber unsupported
                    '%w': '', // weekday unsupported
                    '%W': '', // weeknumber unsupported
                    '%x': '', // locale's date representation
                    '%X': '', // locale's time representation
                    '%y': 'y',
                    '%Y': 'yy',
                    '%Z': 'z',
                    '%%': '%',
                };

            for(var i=0; i < odoo_format.length; i++)
            {
                if(map[odoo_format.substring(i, i+2)])
                {
                    result += map[odoo_format.substring(i, i+2)];
                    i++;
                }
                else
                {
                    result += odoo_format[i];
                }
            }
            return result
        },
        frequency_changed: function(e, noreset)
        {
            var frequency = jQuery(e.currentTarget),
                current_item = frequency
                    .parentsUntil('form', 'table.rule_item');
            current_item.find('[data-visible-freq]').each(function()
            {
                var node = jQuery(this);
                node.toggle(
                    String(node.data('visible-freq')).split(',')
                    .indexOf(frequency.val()) >= 0
                );
            });
            this.input_changed(e, noreset);
        },
        input_changed: function(e, noreset)
        {
            var input = jQuery(e.currentTarget),
                current_item = input
                    .parentsUntil('form', 'table.rule_item'),
                all_values = this.get('value') || [],
                old_values = jQuery.extend(true, [], all_values);
                value = _.findWhere(all_values, {
                    '__id': String(current_item.data('id')),
                });
            if(jQuery.isArray(value[input.attr('name')]))
            {
                var input_value = parseInt(input.val());
                value[input.attr('name')] = _.filter(
                    value[input.attr('name')], function(x) {
                        return x != input_value;
                    });
                if(input.is(':checked'))
                {
                    value[input.attr('name')].push(input_value);
                }
            }
            else if(input.attr('type') == 'datetime')
            {
                value[input.attr('name')] = instance.web.parse_value(
                    input.val(), {type: 'datetime'});
            }
            else
            {
                value[input.attr('name')] = input.val() || undefined;
            }
            if(!noreset)
            {
                this.reset_fields(value, current_item, input.attr('name'));
            }
            this.trigger("change:value", this, {
                oldValue: old_values,
                newValue: all_values,
            });
        },
        toggle_recurrence_type: function(e, noreset)
        {
            var type = jQuery(e.currentTarget),
                current_item = type.parentsUntil('tr', 'td');
            current_item.find('input:not(.rule_ignore_input)').each(function()
            {
                var input = jQuery(this),
                    visible = input.attr('name') == type.attr('value');
                input.toggle(visible);
                if(visible)
                {
                    input.trigger('change', noreset);
                }
            });
        },
        reset_fields: function(rule, current_item, field)
        {
            // for some fields, we should reset some other fields when they
            // were changed
            if(field == 'freq')
            {
                rule.byweekday = [];
                rule.bymonthday = [];
                rule.byyearday = [];
                current_item.find(
                    '[name="byweekday"], [name="bymonthday"], ' +
                    '[name="byyearday"]'
                ).prop('checked', false);
            }
            if(field == 'dtstart')
            {
                rule.byhour = [];
                rule.byminute = [];
                rule.bysecond = [];
                current_item.find(
                    '[name="byhour"], [name="bysecond"], [name="byminute"]'
                ).prop('checked', false);
            }
            if(field == 'until')
            {
                rule.count = undefined;
                current_item.find('[name="count"]').val('0');
            }
            if(field == 'count')
            {
                rule.until = undefined;
                current_item.find('[name="until"]').val('');
            }
        },
        add_rule: function(e)
        {
            var value = this.get('value') || [];
            value.push(this.get_default_rrule());
            this.set('value', value);
            this.reinitialize();
        },
        remove_rule: function(e)
        {
            var value = this.get('value') || [],
                old_value = jQuery.extend(true, [], value),
                current_item = jQuery(e.currentTarget)
                    .parentsUntil('form', 'table.rule_item'),
                current_id = String(current_item.data('id'));

            for(var i = 0; i < value.length; i++)
            {
                if(value[i]['__id'] == current_id)
                {
                    value.splice(i, 1);
                    i--;
                }
            }
            this.trigger("change:value", this, {
                oldValue: old_value,
                newValue: value,
            });
            this.reinitialize();
        },
        get_default_rrule: function()
        {
            return {
                __id: _.uniqueId(),
                type: 'rrule',
                freq: 1,
                count: undefined,
                interval: 1,
                dtstart: instance.datetime_to_str(new Date()),
                byweekday: [],
                bymonthday: [],
                byyearday: [],
            };
        },
        on_timepicker_select: function(datestring, input)
        {
            return this.format_timepicker_value(input.input || input.$input);
        },
        on_timepicker_month_year: function(year, month, input)
        {
            return this.format_timepicker_value(input.input || input.$input);
        },
        format_timepicker_value: function(input)
        {
            input.val(instance.web.format_value(
                input.datetimepicker('getDate'), {type: 'datetime'}));
        },
        format_field_weekday: function(weekday)
        {
            switch(parseInt(weekday))
            {
                case 0: return instance.web._t('Monday');
                case 1: return instance.web._t('Tuesday');
                case 2: return instance.web._t('Wednesday');
                case 3: return instance.web._t('Thursday');
                case 4: return instance.web._t('Friday');
                case 5: return instance.web._t('Saturday');
                case 6: return instance.web._t('Sunday');
            }
        },
        format_field_freq: function(frequency)
        {
            switch(parseInt(frequency))
            {
                case 0: return instance.web._t('Yearly');
                case 1: return instance.web._t('Monthly');
                case 2: return instance.web._t('Weekly');
                case 3: return instance.web._t('Daily');
                case 4: return instance.web._t('Hourly');
                case 5: return instance.web._t('Minutely');
                case 6: return instance.web._t('Secondly');
            }
        },
        format_field_dtstart: function(dtstart)
        {
            return instance.web.format_value(dtstart, {type: 'datetime'});
        },
        format_field_until: function(until)
        {
            return instance.web.format_value(until, {type: 'datetime'});
        },
        format_field_count: function(count)
        {
            if(!count)
            {
                return instance.web._t('Indefinitely');
            }
            return _.str.sprintf(instance.web._t('%s occurrences'), count);
        },
    });
    instance.web.form.widgets.add('rrule', 'instance.field_rrule.FieldRRule');
};
