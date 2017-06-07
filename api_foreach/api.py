# -*- coding: utf-8 -*-
# Copyright 2004-2015 Odoo S.A.
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.api import aggregate, decorator


def foreach(method):
    """ Decorate a record-style method where ``self`` is expected to be a
        singleton instance. The decorated method automatically loops on
        records, and makes a list with the results. In case the method is
        decorated with :func:`returns`, it concatenates the resulting
        instances. Such as
        method::
            @api.foreach
            def method(self, args):
                return self.name
        may be called in both record and traditional styles, like::
            # recs = model.browse(cr, uid, ids, context)
            names = recs.method(args)
            names = model.method(cr, uid, ids, args, context=context)
    """
    def loop(method, self, *args, **kwargs):
        result = [method(rec, *args, **kwargs) for rec in self]
        return aggregate(method, result, self)

    wrapper = decorator(loop, method)
    wrapper._api = 'foreach'
    return wrapper
