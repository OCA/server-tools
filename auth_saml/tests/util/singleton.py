class Singleton(type):
    """
    This is a neat singleton pattern. This was found in a comment on this page:
    http://www.garyrobinson.net/2004/03/python_singleto.html

    to use this, example :
    >>> class C(object):
    ...     __metaclass__ = Singleton
    ...     def __init__(self, foo):
    ...         self.foo = foo

    >>> C('bar').foo
    'bar'

    >>> C().foo
    'bar'

    and your class C is now a singleton, and it is safe to use
    the __init__ method as you usually do...
    """

    def __init__(cls, name, bases, dic):
        super(Singleton, cls).__init__(name, bases, dic)
        cls.instance = None

    def __call__(mcs, *args, **kw):
        if mcs.instance is None:
            mcs.instance = super(Singleton, mcs).__call__(*args, **kw)

        return mcs.instance
