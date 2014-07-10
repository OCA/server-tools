cProfile integration for OpenERP
================================

The module ``profiler`` provides a very basic integration of
the standard ``cProfile`` into OpenERP/Odoo.

Basic usage
-----------

After installation, a new menu "Profiler" gets available in the
administration menu, with four items:

* Start profiling
* Stop profiling
* Dump stats: retrieve from the browser a stats file, in the standard
  cProfile format (see Python documentation and performance wiki page
  for exploitation tips).
* Clear stats

Advantages
----------

Executing Python code under the profiler is not really hard, but this
module allows to do it in OpenERP context such that:

* no direct modification of main server Python code or addons is needed
  (although it could be pretty simple depending on the need)
* subtleties about threads are taken care of. In particular, the
  accumulation of stats over several requests is correct.

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
* UI is currently quite crude, but that's good enough for now

Credit
------

Remotely inspired from ZopeProfiler, although there is no online
visualisation and there may never be one.
