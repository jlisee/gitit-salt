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


def install(name, version=None, refresh=False):
    """
    Install the given cabal package
    """

    # Make sure we have cabal install
    _check_cabal_bin()

    # Refresh as needed
    if salt.utils.is_true(refresh):
        refresh_db()

    # Now lets install the package
    package = name

    res = __salt__['cmd.run']('cabal install %s' % package)

    # TODO: parse results for success
    # Already installed output contains "already installed"
    return res