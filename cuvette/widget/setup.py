from setuptools import setup
import os

APP = ['main.py']
DATA_FILES = []

# Try to find libffi in common locations
LIBFFI_PATHS = [
    '/opt/homebrew/opt/libffi/lib/libffi.8.dylib',  # M1 Mac Homebrew path
    '/usr/local/opt/libffi/lib/libffi.8.dylib',     # Intel Mac Homebrew path
    '/usr/local/lib/libffi.8.dylib',                # Alternative location
]

# Find the first existing libffi path
LIBFFI_PATH = None
for path in LIBFFI_PATHS:
    if os.path.exists(path):
        LIBFFI_PATH = path
        break

if not LIBFFI_PATH:
    raise ValueError("Could not find libffi.8.dylib in any of the expected locations")

OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'frameworks': [LIBFFI_PATH],
    'packages': ['rumps'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)