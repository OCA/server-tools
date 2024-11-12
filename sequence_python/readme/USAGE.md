To use this module, you need to:

- Go to the form view of an ir.sequence record
- Go to the Python tab
- Enable the 'Use Python' checkbox
- Change the default 'number' expression to something more fancy.

Examples:

``` python
# To separate the Odoo-generated number with hyphens eg. 0-0-0-0-1
'-'.join(number_padded)

# To have an UUID as the sequence value
uuid.uuid4().hex

# To use an 8-digit binary number
'{0:#010b}'.format(number + 300)[2:]
```

And so on.
