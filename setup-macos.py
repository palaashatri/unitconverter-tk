"""py2app metadata for the native macOS application bundle."""

import os

from setuptools import setup


APP = ["app.py"]
VERSION = os.environ.get("UNITCONVERTER_VERSION", "0.1.0")
OPTIONS = {
    "argv_emulation": False,
    "iconfile": "assets/brand/icon.icns",
    "includes": ["tkinter"],
    "packages": ["src"],
    "resources": ["assets"],
    "plist": {
        "CFBundleIdentifier": "com.palaashatri.unitconverter",
        "CFBundleName": "Unit Converter",
        "CFBundleDisplayName": "Unit Converter",
        "NSHighResolutionCapable": True,
    },
}


if __name__ == "__main__":
    setup(
        app=APP,
        name="UnitConverter",
        version=VERSION,
        options={"py2app": OPTIONS},
    )
