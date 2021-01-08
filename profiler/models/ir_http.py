# Copyright 2021 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from timeit import default_timer as timer

from odoo import models
from odoo.http import request

from .profiler_profile import ProfilerProfile


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls):
        if request and request.httprequest and request.httprequest.session \
                and getattr(request.httprequest.session, 'oca_profiler', False):
            oca_profiler_id = request.httprequest.session.oca_profiler
            profiler = request.env['profiler.profile'].browse(oca_profiler_id)
            ProfilerProfile.enabled = True
            start = timer()
            with ProfilerProfile.profiling():
                ret = super(IrHttp, cls)._dispatch()
            end = timer()
            ProfilerProfile.enabled = False
            request_line = profiler.sudo().create_request_line()
            request_line.dump_stats()
            request_line.total_time = (end - start) * 1000.0
            return ret
        return super(IrHttp, cls)._dispatch()
