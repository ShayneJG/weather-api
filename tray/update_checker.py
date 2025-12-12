"""
Update checker for Weather Tray application.

Checks GitHub releases for newer versions and notifies the user.
"""
import requests
from version import __version__


GITHUB_REPO = "your-username/weather-api"  # Update this with your GitHub username
RELEASE_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def check_for_updates():
    """
    Check if a newer version is available on GitHub releases.

    :return: Tuple of (update_available: bool, latest_version: str, download_url: str)
    """
    try:
        response = requests.get(RELEASE_API_URL, timeout=5)
        response.raise_for_status()

        release_data = response.json()
        latest_version = release_data.get("tag_name", "").lstrip("v")
        download_url = release_data.get("html_url", "")

        # Compare versions
        if latest_version and _is_newer_version(latest_version, __version__):
            return True, latest_version, download_url

        return False, __version__, ""

    except (requests.exceptions.RequestException, ValueError, KeyError):
        # Silently fail if update check fails
        return False, __version__, ""


def _is_newer_version(latest: str, current: str) -> bool:
    """
    Compare version strings (semantic versioning).

    :param latest: Latest version string (e.g., "1.0.1")
    :param current: Current version string (e.g., "1.0.0")
    :return: True if latest is newer than current
    """
    try:
        latest_parts = tuple(int(x) for x in latest.split("."))
        current_parts = tuple(int(x) for x in current.split("."))
        return latest_parts > current_parts
    except (ValueError, AttributeError):
        return False
