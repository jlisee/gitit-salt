# Author: Joseph Lisee <jlisee@gmail.com>
# License: MIT

# Python Imports
import logging
import os
import shutil

# Project imports
import salt

log = logging.getLogger(__name__)


def _check_cabal_bin():
    """
    Make sure we have cabal installed.
    """

    which_result = __salt__['cmd.which_bin'](['cabal'])
    if which_result is None:
        raise CommandNotFoundError('Could not find a `cabal` binary')


def refresh_db(user=None):
    """
    Downloads the latest hackage dependency information.
    """

    _check_cabal_bin()

    return __salt__['cmd.run_all']('cabal update', runas=user)


def version(*names, **kwargs):
    """
    Returns dict matching package to installed version, None for not installed.
    """

    # Make sure we have cabal install
    _check_cabal_bin()

    # Parse out the user argument
    user = kwargs.get('user', None)

    ret = {}

    for name in names:
        # Get the info about the package
        res = __salt__['cmd.run_all']('cabal info %s' % name, runas=user)

        # Check results
        output = res['stdout']

        # Parse out the installed line
        lines = [l.strip() for l in output.split('\n')]

        for line in lines:
            # Only work on valid liens
            if line.count(':'):
                # Break apart the line into the type and value sections
                parts = line.split(':')
                key = parts[0].strip()
                value = (':'.join(parts[1:])).strip()

                if key == 'Versions installed':
                    # Determine if the package is installed or not
                    if value == '[ Not installed ]':

                        package_name = None
                    else:
                        package_name = [i.strip() for i in value.split(',')]

                    # Store our output
                    ret[name] = package_name

    return ret

# Store an internal version of this to deal with shadowing caused by
# function arguments
_version = version

def install(name, version=None, refresh=False, flags=None, user=None):
    """
    Install the given cabal package.
    """

    # Make sure we have cabal install
    _check_cabal_bin()

    # Make sure we have proper return
    ret = {
        'result' : True,
        'comment' : '',
        'changes' : {}
    }

    # Refresh as needed
    if salt.utils.is_true(refresh):
        res = refresh_db(user=user)

        # Bail out if there was an error
        if 0 != res['retcode']:
            ret['result'] = False
            ret['comment'] = 'update failed: %s' % res['stderr']

            return ret

    # Now lets install the package
    package = name

    # Form our flag string
    if flags:
        flags_str = ' --flags="%s"' % ' '.join(flags)
    else:
        flags_str = ''

    # Form the package string with arguments first
    if version:
        package_str = '%s-%s' % (name, version)
    else:
        package_str = name

    args = (package_str, flags_str)
    res = __salt__['cmd.run_all']('cabal install %s%s' % args, runas=user)

    output = res['stdout']

    # Parse results to determine what we have done
    if 0 == res['retcode']:
        if output.count('Registering '):
            # We have had success parse the package version out the return
            # information, from a string like "Registering bzlib-0.5.0.4..."
            lines = output.split('\n')

            for line in lines:
                if line.count('Registering ') and line.count(package_str):
                    _, name_version = line.split()
                    version_parts = name_version.split('-')
                    raw_version = ''.join(version_parts[1:])
                    version = raw_version[:-3]

                    # Now store the results
                    ret['changes'][name] = version

                    # Drop out
                    break
    else:
        # Failure gather the results and report them
        ret['result'] = False
        ret['comment'] = res['stderr']

    return ret

def uninstall(name, version, user=None):
    # Make sure we have cabal install
    _check_cabal_bin()

    # Make sure we have proper return
    ret = {
        'result' : True,
        'comment' : '',
        'changes' : {}
    }

    # Get the GHC version
    res = __salt__['cmd.run_all']('ghc --numeric-version', runas=user)

    ghc_version = res['stdout']

    # Setup our changes dict to store what havoc we are about to wreck on cabal
    ret['changes'] = {
        'unregistered' : [],
        'removed' : []
    }

    # Un-register the package
    name_version = '%s-%s' % (name, version)
    args = (ghc_version, name_version)

    res = __salt__['cmd.run_all']('ghc-pkg-%s unregister %s' % args,
                                  runas=user)

    # Handle errors
    if 0 != res['retcode']:
        ret['result'] = False
        ret['comment'] = 'ghc-unregister failed: %s' % res['stderr']

        return ret

    # Record removal
    ret['changes']['unregistered'].append('ghc-unregister %s' % name_version)

    # Remove library files
    if user:
        user_dir = os.path.expanduser('~' + user)
    else:
        user_dir = '/root'

    pkg_dir = os.path.join(user_dir, '.cabal', 'lib', name_version)
    version_dir = os.path.join(pkg_dir, 'ghc-%s' % ghc_version)

    shutil.rmtree(version_dir)

    ret['changes']['removed'].append('removed directory: ' + version_dir)

    # Clear out possibly empty directory
    if len(os.listdir(pkg_dir)) == 0:
        shutil.rmtree(pkg_dir)

        ret['changes']['removed'].append('removed directory: ' + pkg_dir)

    # We are done
    ret['comment'] += 'Un-installed %s. ' % name_version

    return ret
