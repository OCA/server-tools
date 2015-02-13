cProfile integration for OpenERP
================================

The module ``profiler`` provides a very basic integration of
the standard ``cProfile`` into OpenERP/Odoo.

Basic usage
-----------

After installation, a player is add on the header bar, with
four items:

|player|

* Start profiling |start_profiling|
* Stop profiling |stop_profiling|
* Download stats: download stats file |dump_stats|
* Clear stats |clear_stats|

Advantages
----------

Executing Python code under the profiler is not really hard, but this
module allows to do it in OpenERP context such that:

* no direct modification of main server Python code or addons is needed
  (although it could be pretty simple depending on the need)
* subtleties about threads are taken care of. In particular, the
  accumulation of stats over several requests is correct.
* Quick access UI to avoid statistics pollution
* Use the standard cProfile format, see Python documentation and performance
  wiki page for exploitation tips. Also do not miss `RunSnakeRun 
  <http://www.vrplumber.com/programming/runsnakerun/>`_ GUI tool to help you to
  interpret it easly.

Caveats
-------

* enabling the profile in one database actually does it for the whole
  instance
* multiprocessing (``--workers``) is *not* taken into account
* currently developped and tested with OpenERP 7.0 only
* no special care for uninstallion : currently a restart is needed to
  finish uninstalling.
* requests not going through web controllers are currently not taken
  into account


Credit
------

Remotely inspired from ZopeProfiler, although there is no online
visualisation and there may never be one.

.. |player| image:: https://bytebucket.org/anybox/odoo_profiler/raw/default/doc/static/player.png
    :alt: Player to manage profiler
.. |start_profiling| image:: https://bytebucket.org/anybox/odoo_profiler/raw/default/doc/static/start_profiling.png
    :alt: Start profiling
    :height: 35px
.. |stop_profiling| image:: https://bytebucket.org/anybox/odoo_profiler/raw/default/doc/static/stop_profiling.png
    :alt: Stop profiling
    :height: 35px
.. |dump_stats| image:: https://bytebucket.org/anybox/odoo_profiler/raw/default/doc/static/dump_stats.png
    :alt: Download cprofile stats file
    :height: 35px
.. |clear_stats| image:: https://bytebucket.org/anybox/odoo_profiler/raw/default/doc/static/clear_stats.png
    :alt: Clear and remove stats file
    :height: 35px
