# Copyright 2018 ACSONE SA/NV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from fnmatch import fnmatch
import hashlib
import os


def _fnmatch(filename, patterns):
    for pattern in patterns:
        if fnmatch(filename, pattern):
            return True
    return False


def _walk(top, exclude_patterns, keep_langs):
    keep_langs = {l.split('_')[0] for l in keep_langs}
    for dirpath, dirnames, filenames in os.walk(top):
        dirnames.sort()
        reldir = os.path.relpath(dirpath, top)
        if reldir == '.':
            reldir = ''
        for filename in sorted(filenames):
            filepath = os.path.join(reldir, filename)
            if _fnmatch(filepath, exclude_patterns):
                continue
            if keep_langs and reldir in {'i18n', 'i18n_extra'}:
                basename, ext = os.path.splitext(filename)
                if ext == '.po':
                    if basename.split('_')[0] not in keep_langs:
                        continue
            yield filepath


def addon_hash(top, exclude_patterns, keep_langs):
    """Compute a sha1 digest of file contents."""
    m = hashlib.sha1()
    for filepath in _walk(top, exclude_patterns, keep_langs):
        # hash filename so empty files influence the hash
        m.update(filepath.encode('utf-8'))
        # hash file content
        with open(os.path.join(top, filepath), 'rb') as f:
            m.update(f.read())
    return m.hexdigest()
