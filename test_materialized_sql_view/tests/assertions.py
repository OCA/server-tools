# -*- coding: utf-8 -*-
# Copyright 2016 Pierre Verkest <pverkest@anybox.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""I didn'nt know if I could introduce new dependences so I sadly copy/paste
a part of the anybox.testting.openerp package here.

High level OpenERP assertions and helpers."""


class OpenErpAssertions(object):
    """Mixin class providing assertion and helper methods to write tests.

    Some of these methods will make less sense with the new API scheduled for
    OpenERP 8, we'll provide them as simple wrappers for backwards compat then.
    """

    def _model_inst(self, model):
        return self.registry(model) if isinstance(model, basestring) else model

    def assertRecord(self, model, rec_id, vals, list_to_set=False, **kw):
        """Fetch and compare a record with the provided values dict.

        This saves a LOT of typing and makes assertion much easier to read
        while avoiding a browse.

        :model: can be either a string (model name) or a model instance
        :rec_id: numeric id of the record to check
        :vals: ``dict`` of expected values. For ``many2one`` fields, just pass
               the expected numeric id.
        :list_to_set: if ``True``, all ``list`` instances in the read record
                      will be converted to ``set`` prior tocomparison
        :kw: any additional keyword arguments are passed on to the underlying
             call(s) of ``assertEqual``.

        Examples:

         - if you already have the model obj as ``users_model``::

             self.assertRecord(users_model, 1, dict(name='Administrator'))

         - in general::

             self.assertRecord('res.users', 1, dict(name='Administrator',
                                                    partner_id=1))
        """
        def normalize(v):
            if list_to_set and isinstance(v, list):
                return set(v)
            return v

        read = self._model_inst(model).read(self.cr, self.uid, rec_id,
                                            vals.keys(), load='_classic_write')
        if isinstance(read, (list, tuple)):
            # happens for some models (seen w/ ir.attachment)
            self.assertEqual(len(read), 1,
                             msg="read() returned a list whose "
                             "length is %d (should be 1)" % len(read))
            read = read[0]

        as_dict = dict((k, normalize(v))
                       for k, v in read.iteritems()
                       if k in vals)
        self.assertEqual(as_dict, vals, **kw)
