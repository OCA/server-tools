import os
import logging
from datetime import datetime
from tempfile import mkstemp
import openerp.addons.web.http as openerpweb
from . import core

logger = logging.getLogger(__name__)


class ProfilerController(openerpweb.Controller):

    _cp_path = '/web/profiler'

    player_state = 'profiler_player_clear'
    """Indicate the state(css class) of the player:

    * profiler_player_clear
    * profiler_player_enabled
    * profiler_player_disabled
    """

    @openerpweb.jsonrequest
    def enable(self, request):
        logger.info("Enabling")
        core.enabled = True
        ProfilerController.player_state = 'profiler_player_enabled'

    @openerpweb.jsonrequest
    def disable(self, request):
        logger.info("Disabling")
        core.enabled = False
        ProfilerController.player_state = 'profiler_player_disabled'

    @openerpweb.jsonrequest
    def clear(self, request):
        core.profile.clear()
        logger.info("Cleared stats")
        ProfilerController.player_state = 'profiler_player_clear'

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
                ('Content-Disposition',
                 'attachment; filename="%s"' % filename),
                ('Content-Type', 'application/octet-stream')
            ], cookies={'fileToken': token})

    @openerpweb.jsonrequest
    def initial_state(self, request):
        user = request.session.model('res.users')
        return {
            'has_player_group': user.has_group('profiler.group_profiler_player'),
            'player_state': ProfilerController.player_state,
        }
