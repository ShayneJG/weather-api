"""
Build script for creating Weather Tray executable using PyInstaller.

Usage:
    python build.py

This will create a standalone executable in the dist/ folder.
"""
import PyInstaller.__main__
import os
import shutil
from version import __version__

# Clean previous builds
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

print(f"Building Weather Tray v{__version__}...")

PyInstaller.__main__.run([
    'main.py',
    '--name=WeatherTray',
    '--onefile',
    '--windowed',
    '--icon=NONE',  # Add an icon file if you have one
    '--add-data=config.json;.',
    '--hidden-import=pystray._win32',
    '--hidden-import=PIL._tkinter_finder',
    f'--distpath=dist/v{__version__}',
    '--clean',
])

print(f"\nBuild complete! Executable located in: dist/v{__version__}/WeatherTray.exe")
