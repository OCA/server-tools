# -*- coding: utf-8 -*-
# Copyright 2021 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from timeit import default_timer as timer
from cProfile import Profile

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls):
        if request and request.httprequest and request.httprequest.session \
                and getattr(request.httprequest.session, 'oca_profiler', False):
            profile = Profile()
            profile.enable()
            try:
                oca_profiler_id = request.httprequest.session.oca_profiler
                RequestLine = request.env['profiler.profile.request.line']
                profiler = request.env['profiler.profile'].browse(oca_profiler_id)
                profile = Profile()
                start = timer()
                ret = False
                profile.enable()
                ret = super(IrHttp, cls)._dispatch()
                profile.disable()
                end = timer()
            except:  # noqa
                profile.disable()
                raise
            try:
                cprofile_fname, cprofile_path = RequestLine.dump_stats(profile)
                request_line = profiler.sudo().create_request_line()
                request_line.dump_stats_db(cprofile_fname, cprofile_path)
                request_line.total_time = (end - start) * 1000.0
            except:  # noqa
                pass
            return ret
        return super(IrHttp, cls)._dispatch()
