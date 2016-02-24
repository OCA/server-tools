.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========
Profiler
========

Integration of cProfile and PgBadger.

Installation
============

To install this module, you need the following requirements:

* Install `pgbadger <http://dalibo.github.io/pgbadger/>`_ binary package.
* Install `pstats_print2list <https://pypi.python.org/pypi/pstats_print2list>`_ python package.
* Set `PG_LOG_PATH` environment variable to know location of the `postgresql.log` file by default is `/var/lib/postgresql/9.X/main/pg_log/postgresql.log`
* Enable postgresql logs from postgresql's configuration file (Default location for Linux Debian is `/etc/postgresql/*/main/postgresql.conf`)
  - Add the following lines at final (A postgresql restart is required `/etc/init.d/postgresql restart`)

.. code-block:: text

 logging_collector=on
 log_destination='stderr'
 log_directory='pg_log'
 log_filename='postgresql.log'
 log_rotation_age=0
 log_checkpoints=on
 log_hostname=on
 log_line_prefix='%t [%p]: [%l-1] db=%d,user=%u '


Configuration
=============

By default profiler module adds two system parameters
    - exclude_fnames > '/.repo_requirements,~/odoo-8.0,/usr/,>'
    - exclude_query > 'ir_translation'.

These parameters can be configurated in order to exclude some outputs from
profiling stats or pgbadger output.

Usage
=====

After installation, a player is add on the header bar, with following buttons:

    - .. figure:: static/description/player.png
       :alt: Player to manage profiler


* Start profiling
    - .. figure:: static/description/start_profiling.png
       :alt: Start profiling
       :height: 35px
* Stop profiling
    - .. figure:: static/description/stop_profiling.png
       :alt: Stop profiling
       :height: 35px
* Download stats: download stats file
    - .. figure:: static/description/dump_stats.png
       :alt: Download cprofile stats file
       :height: 35px
* Clear stats
    - .. figure:: static/description/clear_stats.png
       :alt: Clear and remove stats file
       :height: 35px


Credits
=======

Contributors
------------

* Georges Racinet <gracinet@anybox.fr>
   - Remotely inspired from ZopeProfiler, although there is no online visualisation and there may never be one.
* Moisés López <moylop260@vauxoo.com>
* Hugo Adan <hugo@vauxoo.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
