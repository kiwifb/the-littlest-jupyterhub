"""
Miscellaneous functions useful in at least two places unrelated to each other
"""

import logging
import re
import subprocess

# Copied into bootstrap/bootstrap.py. Make sure these two copies are exactly the same!
import pluggy

from tljh import hooks


# This function is needed also by the bootstrap script that starts this
# installer script. Make sure its replica at bootstrap/bootstrap.py stays in
# sync with this version!
def run_subprocess(cmd, *args, **kwargs):
    """
    Run given cmd with smart output behavior.

    If command succeeds, print output to debug logging.
    If it fails, print output to info logging.

    In TLJH, this sends successful output to the installer log,
    and failed output directly to the user's screen
    """
    logger = logging.getLogger("tljh")
    printable_command = " ".join(cmd)
    logger.debug("Running %s", printable_command)
    proc = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, *args, **kwargs
    )
    if proc.returncode != 0:
        # Our process failed! Show output to the user
        logger.error(
            "Ran {command} with exit code {code}".format(
                command=printable_command, code=proc.returncode
            )
        )
        logger.error(proc.stdout.decode())
        raise subprocess.CalledProcessError(cmd=cmd, returncode=proc.returncode)
    else:
        # This goes into installer.log
        logger.debug(
            "Ran {command} with exit code {code}".format(
                command=printable_command, code=proc.returncode
            )
        )
        # This produces multi line log output, unfortunately. Not sure how to fix.
        # For now, prioritizing human readability over machine readability.
        logger.debug(proc.stdout.decode())


def get_plugin_manager():
    """
    Return plugin manager instance
    """
    # Set up plugin infrastructure
    pm = pluggy.PluginManager("tljh")
    pm.add_hookspecs(hooks)
    pm.load_setuptools_entrypoints("tljh")

    return pm


def parse_version(version_string):
    """Parse version string to tuple

    Finds all numbers and returns a tuple of ints
    _very_ loose version parsing, like the old distutils.version.LooseVersion
    """
    # return a tuple of all the numbers in the version string
    # always succeeds, even if passed nonsense
    return tuple(int(part) for part in re.findall(r"\d+", version_string))
