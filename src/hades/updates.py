"""Version update checker for Hades software.

Provides a function to check for the latest release version of the Hades software on GitHub and compare it with the current version.
"""

import urllib.request
import json

def check_for_updates(gui=False) -> None:
    """
    Checks for updates to the Hades software by querying the GitHub API for the latest release version.
    If a newer version is available, it prints a message to the console. If the GUI is enabled, returns a boolean and the newest version string.

    Parameters
    ----------
    gui : bool, optional
        If True, the function will return a tuple (update_available, latest_version) instead of printing to the console.
        Default is False.
    """
    version = "0.9.1"
    url = "https://api.github.com/repos/Jack6228/Hades/releases/latest"

    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read().decode())
            latest_version = data['tag_name']
            # Strip the leading 'v' if present
            if latest_version.startswith('v'):
                latest_version = latest_version[1:]

        cur = [int(x) for x in version.split('.')]
        latest = [int(x) for x in latest_version.split('.')]

        if cur < latest:
            if gui:
                return True, latest_version
            else:
                print(f"A newer version of Hades is available: v{latest_version}. You are currently using v{version}.")
                print(f" > To update, run: pip install --upgrade hades-obol")

        else:
            if gui:
                return False, latest_version
            else:
                print(f"You are using the latest version of Hades: v{version}.")

    except Exception as e:
        if gui:
            return False, None
        else:
            print(f"Check for updates failed, check manually at:\n > https://github.com/Jack6228/Hades/releases/latest\n > Your current version is v{version}.")
