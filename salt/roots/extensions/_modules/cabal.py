# Author: Joseph Lisee <jlisee@gmail.com>
# License: MIT

# Python Imports
import logging

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


def refresh_db():
    """
    Downloads the latest hackage dependency information.
    """

    _check_cabal_bin()

    res = __salt__['cmd.run']('cabal update')

    return res


def version(*names):
    """
    Returns dict matching package to installed version, None for not installed.
    """

    _check_cabal_bin()

    res = {}

    for name in names:
        # Get the info about the package
        output = __salt__['cmd.run']('cabal info %s' % name)

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

                        input = None
                    else:
                        input = value

                    # Store our output
                    res[name] = input

    return res


def install(name, version=None, refresh=False, flags=None):
    """
    Install the given cabal package.
    """

    # Make sure we have cabal install
    _check_cabal_bin()

    # Refresh as needed
    if salt.utils.is_true(refresh):
        refresh_db()

    # Now lets install the package
    package = name

    # Form our flag string
    if flags:
        flags_str = ' --flags="%s"' % ' '.join(flags)
    else:
        flags_str = ''

    args = (package, flags_str)
    res = __salt__['cmd.run']('cabal install %s%s' % args)

    # TODO: parse results for success better
    ret = {
        'result' : True,
        'comment' : '',
        'changes' : {}
    }

    if res.count('Registering '):
        # We have had success parse the package version out the return
        # information, from a string like "Registering bzlib-0.5.0.4..."
        lines = res.split('\n')

        for line in lines:
            if line.count('Registering ') and line.count(name):
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
        ret['comment'] = res


    return ret
