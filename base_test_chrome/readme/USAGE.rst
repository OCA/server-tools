To use this module, you need to:

#. depend on it
#. import ``openerp.addons.base_test_chrome.common.HttpCase``
#. use this the same way you'd use ``openerp.tests.common.HttpCase``

Notes:

* while the phantomjs code accepts any truthy ready object, this code
  explicitly looks for a boolean ``true`` - use ``!!$your_original_code``
  to transform it into a boolean if it isn't
