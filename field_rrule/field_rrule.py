# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from dateutil.rrule import rrule, rruleset
from openerp import fields, models
_DATETIME_FIELDS = ['_until', '_dtstart']
_SCALAR_FIELDS = [
    '_wkst', '_cache', '_until', '_dtstart', '_count', '_freq', '_interval',
]
_ZERO_IS_NOT_NONE = ['_freq']


class SerializableRRuleSet(rruleset, list):
    """Getting our rule set json stringified is tricky, because we can't
    just inject our own json encoder. Now we pretend our set is a list,
    then json.dumps will try to iterate, which is why we can do our specific
    stuff in __iter__"""
    def __init__(self, *args):
        self._rrule = []
        super(SerializableRRuleSet, self).__init__(self)
        for arg in args:
            self.rrule(arg)

    def __iter__(self):
        for rule in self._rrule:
            yield dict(type='rrule', **{
                key[1:]:
                fields.Datetime.to_string(getattr(rule, key))
                if key in _DATETIME_FIELDS
                else
                [] if getattr(rule, key) is None and key not in _SCALAR_FIELDS
                else
                list(getattr(rule, key)) if key not in _SCALAR_FIELDS
                else getattr(rule, key)
                for key in [
                    '_byhour', '_wkst', '_bysecond', '_bymonthday',
                    '_byweekno', '_bysetpos', '_cache', '_bymonth',
                    '_byyearday', '_byweekday', '_byminute',
                    '_until', '_dtstart', '_count', '_freq', '_interval',
                    '_byeaster',
                ]
            })
        # TODO: implement rdate, exrule, exdate

    def __call__(self, default_self=None):
        """convert self to a proper rruleset for iteration.
        If we use defaults on our field, this will be called too with
        and empty recordset as parameter. In this case, we need self"""
        if isinstance(default_self, models.BaseModel):
            return self
        result = rruleset()
        result._rrule = self._rrule
        result._rdate = self._rdate
        result._exrule = self._exrule
        result._exdate = self._exdate
        return result

    def __nonzero__(self):
        return bool(self._rrule)

    def __repr__(self):
        return ', '.join(str(a) for a in self)

    def __getitem__(self, key):
        return rruleset.__getitem__(self(), key)

    def __getslice__(self, i, j):
        return rruleset.__getitem__(self(), slice(i, j))

    def __ne__(self, o):
        return not self.__eq__(o)

    def __eq__(self, o):
        return self.__repr__() == o.__repr__()

    def between(self, after, before, inc=False):
        return self().between(after, before, inc=inc)

    def after(self, dt, inc=False):
        return self().after(dt, inc=inc)

    def before(self, dt, inc=False):
        return self().before(dt, inc=inc)

    def count(self):
        return self().count()


class FieldRRule(fields.Serialized):
    def convert_to_cache(self, value, record, validate=True):
        result = SerializableRRuleSet()
        if not value:
            return result
        if isinstance(value, SerializableRRuleSet):
            return value
        assert isinstance(value, list), 'An RRULE\'s content must be a list'
        for data in value:
            assert isinstance(data, dict), 'The list must contain dictionaries'
            assert 'type' in data, 'The dictionary must contain a type'
            data_type = data['type']
            data = {
                key: fields.Datetime.from_string(value)
                if '_%s' % key in _DATETIME_FIELDS
                else map(int, value)
                if value and '_%s' % key not in _SCALAR_FIELDS
                else int(value) if value
                else None if not value and '_%s' % key not in _ZERO_IS_NOT_NONE
                else value
                for key, value in data.iteritems()
                if key != 'type'
            }
            if data_type == 'rrule':
                result.rrule(rrule(**data))
            # TODO: implement rdate, exrule, exdate
            else:
                raise ValueError('Unknown type given')
        return result
