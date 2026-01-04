BLACKLIST_MODULES = [
    "payment_alipay",
    "payment_ogone",
    "payment_payulatam",
    "payment_payumoney",
]

# the hw_* modules are not affected by a migration as they don't
# contain any ORM functionality, but they do start up threads that
# delay the process and spit out annoying log messages continuously.

# We also don't want to analyze tests modules
BLACKLIST_MODULES_STARTS_WITH = ["hw_", "test_"]

BLACKLIST_MODULES_ENDS_WITH = ["_test"]
