"""py2app metadata for the native macOS application bundle."""

from setuptools import setup


APP = ["app.py"]
OPTIONS = {
    "argv_emulation": False,
    "includes": ["tkinter"],
    "packages": ["src"],
}


if __name__ == "__main__":
    setup(
        app=APP,
        name="UnitConverter",
        options={"py2app": OPTIONS},
    )
