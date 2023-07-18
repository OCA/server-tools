================
Import Processor
================

This module enables users to easily import JSON, CSV, or XML files. User can write code snippets in the pre-processor, processor, and post-processor to manipulate the import file.

**Table of contents**

.. contents::
   :local:

Installation
=============

* To install this module, simply search import_processor in Apps search view and install the module.

Usage
======

Concepts
~~~~~~~~

This module provides a set of pre-defined functions and wizards to facilitate importing data into Odoo.

The module offers predefined variables that can be used when writing code snippets in the view.

Note: Only pre-defined variables can be used in code snippets.

The module consists of three main processes:

1. Pre-Processor:
   - At this stage, you can define code snippets that will be executed before importing the records in the view.

2. Processor:
   - At this stage, you can define code snippets that will be executed during the import process.

3. Post-Processor:
   - At this stage, you can define code snippets that will be executed after the records have been imported.

Use Cases
~~~~~~~~~

1. Navigate to Settings > Technical > Import Processors and create a new Import Processor for CSV files with the following settings:
   - Name: "CSV"
   - File Type: CSV
   - User can also define Chunk size if necessary
   - Write the necessary code snippets in the Pre-Processor, Processor, and Post-Processor pages at the bottom of the form view.

2. Save the record and go to Contacts > Favorites > Import Processor.

3. In the Import Processor wizard, select the field Processor as "CSV" from the drop-down menu and click the "Upload your file" button. Choose the desired CSV file and then press the "Import" button.

- Similarly, you can add Import Processors for JSON and XML files by selecting the appropriate File type in the Processor field.

Credits
=======

Authors
~~~~~~~

* initOS

Contributors
~~~~~~~~~~~~

* Dhara Solanki <dhara.solanki@initos.com>
