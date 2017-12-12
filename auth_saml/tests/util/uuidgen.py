"""Utilities to handle unique ID generation.
"""

import uuid


def genUuid(max_chars=None):
    """Generate a unique ID and return its hex string representation.

    :param max_chars: Maximum amount of characters to return (might not be a
    true UUID then...).
    :type max_chars: Integer.

    :rtype: String.
    """

    ret = uuid.uuid4().hex

    if max_chars is not None:
        ret = ret[:max_chars]

    return ret
