# Author: Joseph Lisee <jlisee@gmail.com>
# License: MIT

# Python Imports
import logging
import os

# Project imports
import salt


log = logging.getLogger(__name__)

def __gen_rtag():
    """
    Return the location of the refresh tag.
    """
    return os.path.join(__opts__['cachedir'], 'cabal_refresh')


def installed(name, version=None, refresh=False, flags=None, user=None):
    """
    Make sure the desired cabal package is installed.

    Usage::

        zlib:
          pkg.installed:
            - version: 0.5.4.1
    """

    # Parse arguments
    if flags is None:
        flags =[]

    # Setup default return value
    ret = {
        'name' : name,
        'result' : True,
        'comment' : 'none',
        'changes' : {},
        }

    # Check if we have the package installed and exit if we do
    pkg_info = __salt__['cabal.version'](name, user=user)
    installed_versions = pkg_info.get(name, None)

    package_installed = False

    if (version and installed_versions) and (version in installed_versions):
        package_installed = True
    elif installed_versions and not version:
        package_installed = True

    if package_installed:
        version_str = ', '.join(installed_versions)
        msg = 'Package version(s): %s already installed' % version_str
        ret['comment'] = msg
        return ret

    # Determine if we need to do a refresh of the index
    rtag = __gen_rtag()
    do_refresh = salt.utils.is_true(refresh) or os.path.isfile(rtag)

    # Install our package
    res = __salt__['cabal.install'](name,
                                    version=version,
                                    refresh=do_refresh,
                                    flags=flags,
                                    user=user)

    if res['result']:
        # Report results
        ret['comment'] = '%s package installed' % name

        installed_version = res['changes'].get(name, 'ERROR')
        args = (name, installed_version)

        changes = {
            'installed' : 'cabal package %s-%s installed' % args
        }

        if flags:
            changes['flags'] = flags

        ret['changes'] = changes
    else:
        # Copy over error message from lower level command
        ret['result'] = False
        ret['comment'] = res['comment']

    # Clean up refresh tag file if needed
    if do_refresh and os.path.isfile(rtag):
        os.remove(rtag)

    return ret

def absent(name, version=None, user=None):
    """
    Make sure the particular package is no longer installed.
    """

    # Setup default return value
    ret = {
        'name' : name,
        'result' : True,
        'comment' : '',
        'changes' : {},
        }

    # Look up what versions of the package are installed
    installed = __salt__['cabal.version'](name, user=user)

    versions_to_remove = []

    # Look up installed versions
    if version:
        # User specified a version so just uninstall that one
        versions_to_remove = [version]
    else:
        # No version specified remove all found packages
        versions_to_remove = installed.get(name, [])

    # Bail out if we don't have any packages to remove
    if len(versions_to_remove) == 0:
        if len(installed) == 0:
            ret['comment'] = 'Package %s not installed' % name
        elif version:
            ret['comment'] = 'Package %s-%s not installed' % (name, version)
        ret['result'] = True

        return ret

    # Remove all the given versions
    for cur_version in versions_to_remove:
        res = __salt__['cabal.uninstall'](name, version=cur_version, user=user)

        # Inform the user of the changes we have made to there system
        ret['comment'] += res['comment'] + '\n'

        for key, value in res['changes'].iteritems():
            ret['changes'].setdefault(key, []).extend(value)

        # Bail out with an error if we fail to uninstall a package
        if not res['result']:
            ret['result'] = False
            return ret

    return ret

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
