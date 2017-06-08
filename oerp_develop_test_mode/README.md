OpenERP - Develop - Test Mode
=============================

OpenERP / Odoo Module which help you to set the database for Test or Development mode.

Features:
---------

    * Set-up Test or Development environment at the level of database.
    * Provides unique mode-bar for notifying either database is in Develop mode or Test mode.
    * Mail restriction for outgoing mails.

Usage Of the Module:
====================

Install ``oerp_develop_test_mode`` module:

![oerp_install.png](https://bitbucket.org/repo/RojGB4/images/2194980438-oerp_install.png)

Settings Menu
-------------

In **Settings -> Configuration -> General Settings -> Options** we can see the options as follows:

    * Active Test Mode
    * Active Develop Mode

![2setting.png](https://bitbucket.org/repo/RojGB4/images/28653118-2setting.png)

Setting-up Develop Mode
-----------------------

* In following way we can set-up Development environment in our database.
* Settings -> Configuration -> General Settings -> Options -> **Active Develop Mode**. Then Click on ``Apply``
* Also, this mode is a default mode when we install this module in any database.

![4setting_develope.png](https://bitbucket.org/repo/RojGB4/images/2951521035-4setting_develope.png)

Setting-up Test Mode
--------------------

* In following way we can set-up Development environment in our database.
* Settings -> Configuration -> General Settings -> Options -> **Active Test Mode**. Then Click on ``Apply``

![3setting_test.png](https://bitbucket.org/repo/RojGB4/images/3927111703-3setting_test.png)

Working in Development Environment
----------------------------------

* This module give look and feel to the developer that the current database is for Development.
* Here, Company logo has not been replaced but just to improve effectiveness of module "Development" or "Test" is there in place of Company logo.
* If we switch through anywhere in database it notifies that the current database is Development database as follows:

![6move_develop.png](https://bitbucket.org/repo/RojGB4/images/3474429992-6move_develop.png)

Working in Test Environment
---------------------------

- This module give look and feel to the developer that the current database is for Testing.
- If we switch through anywhere in database it notifies that the current database is Test database as follows:

![5move_test.png](https://bitbucket.org/repo/RojGB4/images/2650653536-5move_test.png)

Mail Restriction
----------------

- This module also provides the functionality of restricting outgoing mail where the database is either in Develop mode or in Test mode.

![7mail_failed.png](https://bitbucket.org/repo/RojGB4/images/908066765-7mail_failed.png)