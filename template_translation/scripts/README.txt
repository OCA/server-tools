Receive hc.registration data from portal HC
==================================================

This script automates sending test requests to HC api

The project contains:
- README.txt: This file.
- api_login.py: The Python 3 script to test authentication.
- test_registrations.py: The Python 3 script to test the api itself.
- test.ini: Configuration parameters for request (database, user, etc)
- requirements.txt: The file listing the dependencies.

Installation
------------

Install the dependency (only `requests`) in your Python 3 environment:

    $ virtualenv -p python3 env
    ...
    $ source env/bin/activate
    (env) $ pip install -r requirements.txt
    ...
    Successfully installed certifi-2020.6.20 chardet-3.0.4 idna-2.10 requests-2.24.0 urllib3-1.25.10

Now, you can run the script:

    (env) $ python3 test_registrations.py -p password
    where password is the password for api_user
