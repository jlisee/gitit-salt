# Author: Joseph Lisee <jlisee@gmail.com>
# License: MIT

# Python Imports
import logging

log = logging.getLogger(__name__)

def __gen_rtag():
    """
    Return the location of the refresh tag.
    """
    return os.path.join(__opts__['cachedir'], 'cabal_refresh')


def installed(name, version=None, refresh=False):
    """
    Make sure the desired cabal package is installed.

    Usage::

        zlib:
          pkg.installed:
            - version: 0.5.4.1
    """
    pass


def mod_init(low):
    """
    Set a flag to tell the install function to replace the database.  This
    ensures we only refresh the database once.
    """

    ret = True

    if low['fun'] == 'installed' or low['fun'] == 'latest':
        rtag = __gen_rtag()

        if not os.path.exists(rtag):
            salt.utils.fopen(rtag, 'w+').write('')

        return ret

    return False
