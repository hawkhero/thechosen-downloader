# -*- coding: utf-8 -*-
# setup.py
import sys
from setuptools import setup
import os
import shutil
from pathlib import Path

# --- Configuration ---
APP_NAME = "The Chosen Downloader"
APP_SCRIPT = 'src/thechosen_downloader/cli.py'
VERSION = '1.0.0'
ICON_FILE = 'assets/icon.icns'
BUNDLE_ID = 'com.hawk.thechosendownloader'
COPYRIGHT = f'Copyright © {os.getenv("USER", "User")} 2025, All Rights Reserved'

# --- py2app Options ---
OPTIONS = {
    'argv_emulation': True,
    'iconfile': ICON_FILE,
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleShortVersionString': VERSION,
        'CFBundleVersion': VERSION,
        'CFBundleIdentifier': BUNDLE_ID,
        'NSHumanReadableCopyright': COPYRIGHT,
    },
    'packages': ['customtkinter', 'yt_dlp', 'playwright', 'bs4'],
    'resources': ['season1.json'],
    'includes': [
        'playwright._impl.__pyinstaller.hook-playwright',
        'playwright._impl.__pyinstaller.hook-playwright.sync_api',
        'playwright._impl.__pyinstaller.hook-playwright.async_api',
        'PIL'
    ],
    'excludes': ['setuptools', 'pip', 'wheel'],
    'bdist_base': 'build',
}

# --- Asset directory ---
if not os.path.exists('assets'):
    os.makedirs('assets')
if not os.path.exists(ICON_FILE):
    print(f"Warning: Icon file '{ICON_FILE}' not found. A placeholder will be used.")
    shutil.copy(shutil.which('python'), 'assets/icon.icns')


# --- Setup ---
setup(
    app=[APP_SCRIPT],
    name=APP_NAME,
    version=VERSION,
    data_files=[],
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)