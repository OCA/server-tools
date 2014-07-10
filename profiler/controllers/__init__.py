import os
import logging
from datetime import datetime
from tempfile import mkstemp
import openerp.addons.web.http as openerpweb
from .. import core

logger = logging.getLogger(__name__)


class ProfilerController(openerpweb.Controller):

    _cp_path = '/web/profiler'

    @openerpweb.jsonrequest
    def enable(self, request):
        logger.info("Enabling")
        core.enabled = True

    @openerpweb.jsonrequest
    def disable(self, request):
        logger.info("Disabling")
        core.disabled = True

    @openerpweb.jsonrequest
    def clear(self, request):
        core.profile.clear()
        logger.info("Cleared stats")

    @openerpweb.httprequest
    def dump(self, request, token):
        """Provide the stats as a file download.

        Uses a temporary file, because apparently there's no API to
        dump stats in a stream directly.
        """
        handle, path = mkstemp(prefix='profiling')
        core.profile.dump_stats(path)
        stream = os.fdopen(handle)
        os.unlink(path)  # TODO POSIX only ?
        stream.seek(0)
        filename = 'openerp_%s.stats' % datetime.now().isoformat()
        # can't close the stream even in a context manager: it'll be needed
        # after the return from this method, we'll let Python's GC do its job
        return request.make_response(
            stream,
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"' % filename),
                ('Content-Type', 'application/octet-stream')
            ], cookies={'fileToken': int(token)})
