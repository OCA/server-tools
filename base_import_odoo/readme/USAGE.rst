To use this module, you need to:

#. go to an import configuration and hit the button ``Run import``
#. be patient, this creates a cronjob which will start up to a minutes afterwards
#. reload the form, as soon as the cronjob runs you'll see a field ``Progress`` that lets you inspect what was imported already
#. note that the cronjob also resets the password as soon as it has read it. So for a subsequent import, you'll have to fill it in again
#. running an import a second time won't duplicate data, it should recognize records imported earlier and just update them
