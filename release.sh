#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting release build process..."

# 1. Clean up previous builds
echo "Cleaning up previous build artifacts..."
rm -rf build dist
echo "Clean up complete."

# 2. Run PyInstaller to create the .app bundle
echo "Running PyInstaller to create the .app bundle..."
uv run pyinstaller TheChosenDownloader.spec --noconfirm
echo "PyInstaller build complete. .app bundle created in dist/."

# 3. Create the .dmg file using create-dmg
echo "Creating the .dmg installer..."
create-dmg \
  --volname "The Chosen Downloader" \
  --window-pos 200 120 \
  --window-size 800 400 \
  "dist/The-Chosen-Downloader-Reduced.dmg" \
  "dist/TheChosenDownloader.app"
echo ".dmg creation complete. The installer is in dist/The-Chosen-Downloader-Reduced.dmg"

echo "Release build process finished successfully!"

