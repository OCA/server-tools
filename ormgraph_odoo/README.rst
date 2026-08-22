================================================
ORMGraph — ORM Architecture & ERD Studio for Odoo
================================================

.. 
   Author: Piyush Kumar (iam-piyush)
   License: LGPL-3

ORMGraph is an interactive architecture intelligence, Entity Relationship Diagram (ERD) visualizer, and relational dependency pathfinder studio for Odoo.

**Table of contents**

.. contents::
   :local:

Key Capabilities
================

* **Module-First Architecture Canvas**: Explore models and foreign relations module-by-module without freezing the browser.
* **Interactive ERD Table Cards**: Visual schema cards with color-coded field badges for Many2one, One2many, Many2many, and computed fields.
* **BFS Multi-Hop Pathfinder**: Calculates shortest relational routes between any two models and generates ORM dot-notation (e.g. ``partner_id.currency_id``).
* **Smart Multi-Cluster ZIP Exporter**: Auto-detects large models (> 20 models), clusters them into Hub sub-graphs, and exports high-resolution diagrams in a ZIP archive.
* **1-Click Model Stat Button**: Direct "Architecture Visualizer" smart button integrated on any model form inside ``Settings ➔ Technical ➔ Database Structure ➔ Models``.
* **Architecture Health**: Detect circular dependencies and explore strongly connected components.

Installation
============

1. Place the ``ormgraph_odoo`` folder inside your Odoo addons path.
2. Update the apps list via **Apps ➔ Update Apps List**.
3. Search for **ORMGraph** and click **Install**.

Usage
=====

1. Open **ORMGraph** from the main Odoo Apps Drawer or click the smart button in any model's form view.
2. Select any module from the left sidebar to generate its live relational jaal.
3. Switch between **Graph View**, **ERD Cards**, **Pathfinder**, and **Architecture Health**.
4. Click **Export PNG** or **ZIP Bundle** to download diagrams.

Credits
=======

Authors
~~~~~~~

* Piyush Kumar (`iam-piyush <https://github.com/iam-piyush>`_)
* Website: `iampiyush.one <https://iampiyush.one>`_

Maintainers
~~~~~~~~~~~

This module is maintained by Piyush Kumar.
