#!/usr/bin/env python3
"""
Script to package the application for Windows using PyInstaller
This requires PyInstaller to be installed: pip install pyinstaller
"""
import os
import platform
import subprocess
import sys

def main():
    # Ensure we're using the right path separator for the target platform
    separator = ';' if 'windows' in sys.argv or '--windows' in sys.argv else ':'

    # Define the PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'ludum',
        '--specpath', '.',
        '--workpath', './build',
        '--distpath', './dist',
    ]

    # Add data files with the appropriate separator
    resources = ['assets', 'audio', 'sprites', 'config', 'engine', 'objects', 'rain', 'utils']
    for resource in resources:
        cmd.append(f'--add-data={resource}{separator}{resource}')

    # Add the main script
    cmd.append('game.py')

    # Run PyInstaller
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"Executable created in dist/")

if __name__ == '__main__':
    main()