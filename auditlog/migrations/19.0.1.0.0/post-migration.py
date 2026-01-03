def migrate(cr, version):
    """19.0: state 'subscribed' is renamed to 'confirmed'"""
    cr.execute(
        "update auditlog_rule set state = 'confirmed' where state = 'subscribed';"
    )
