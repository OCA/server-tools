1.  You can create an index for the name field of res.partner.

2.  In the search you can use:

    `self.env['res.partner'].search([('name', '%', 'Jon Smit')])`

3.  In this example the function will return positive result for John
    Smith or John Smit.

4.  You can tweak the number of strings to be returned by adjusting the
    set limit (default: 0.3). NB: Currently you have to set the limit by
    executing the following SQL statement:

    `self.env.cr.execute("SELECT set_limit(0.2);")`

For further questions read the Documentation of the
[pg_trgm](https://www.postgresql.org/docs/current/static/pgtrgm.html)
module.

## Usage with demo data

There are some demo data that allow you to test functionally this module
if you are in a **demo** database. The steps are the following:

1.  Go to *Contacts* and type the text **Jon Smith** or **Smith John**
    in the search box and select **Search Display Name for: ...**
2.  You will see two contacts, and they are the ones with display names
    **John Smith** and **John Smizz**.
