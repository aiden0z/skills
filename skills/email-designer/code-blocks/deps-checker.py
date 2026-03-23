"""
Dependency Checker — Detect and Install Optional Dependencies
==============================================================
Email designer core is stdlib-only. Charts and image processing
require optional packages that this script auto-installs on demand.

Usage by Agent:
    1. Determine which features are needed (charts, images)
    2. Run check_and_install(['charts', 'images'])
    3. If all available → proceed silently
    4. If install fails → offer degraded mode to user

Dependencies: Python stdlib only (subprocess, importlib)
"""

import subprocess
import sys


# Feature → required packages mapping
FEATURE_DEPS = {
    "charts": [
        ("plotly", "plotly>=6.5.0"),
        ("kaleido", "kaleido>=1.2.0"),
    ],
    "images": [
        ("PIL", "pillow>=12.0.0"),
    ],
}


def _is_available(import_name: str) -> bool:
    """Check if a package is importable."""
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def _install(packages: list) -> tuple:
    """Install packages via pip. Returns (installed, failed) lists."""
    installed = []
    failed = []
    for pkg in packages:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            installed.append(pkg)
        except subprocess.CalledProcessError:
            failed.append(pkg)
    return installed, failed


def check_and_install(features: list) -> dict:
    """Check and install dependencies for requested features.

    Args:
        features: list of 'charts', 'images', or both

    Returns:
        {
            'available': ['charts', 'images'],   # features ready to use
            'installed': ['plotly>=6.5.0', ...],  # packages just installed
            'failed': ['kaleido>=1.2.0', ...],    # packages that failed to install
        }
    """
    available = []
    all_installed = []
    all_failed = []

    for feature in features:
        deps = FEATURE_DEPS.get(feature, [])
        if not deps:
            continue

        missing_packages = []
        for import_name, pip_name in deps:
            if not _is_available(import_name):
                missing_packages.append(pip_name)

        if not missing_packages:
            available.append(feature)
            continue

        # Try to install missing packages
        installed, failed = _install(missing_packages)
        all_installed.extend(installed)
        all_failed.extend(failed)

        if not failed:
            available.append(feature)

    return {
        "available": available,
        "installed": all_installed,
        "failed": all_failed,
    }


def check_only(features: list) -> dict:
    """Check availability without installing. Returns same format as check_and_install."""
    available = []
    missing = []

    for feature in features:
        deps = FEATURE_DEPS.get(feature, [])
        feature_ok = True
        for import_name, pip_name in deps:
            if not _is_available(import_name):
                missing.append(pip_name)
                feature_ok = False
        if feature_ok:
            available.append(feature)

    return {"available": available, "missing": missing}
