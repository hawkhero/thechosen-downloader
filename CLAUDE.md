<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# TheChosenDownloader - Project Guide

## Overview
macOS app to download episodes from The Chosen streaming platform. Has both CLI and GUI modes.

## Key Files
- `src/thechosen_downloader/cli.py` - CLI entry point, also handles GUI launch
- `src/thechosen_downloader/gui.py` - CustomTkinter GUI
- `TheChosenDownloader-GUI.spec` - Lightweight GUI-only build (~136MB)
- `TheChosenDownloader-Full.spec` - Full build with playwright for CLI URL extraction (~267MB)
- `release.sh` - Build script (uses GUI spec, creates .app and .dmg)
- `season1.json` - Episode metadata (bundled with app)

## Build Commands

```bash
# Build lightweight GUI-only .app bundle (recommended for distribution)
./release.sh

# Or manually:
source .venv/bin/activate
pyinstaller TheChosenDownloader-GUI.spec -y   # 136MB, no playwright

# Full build with CLI URL extraction (for developers)
pyinstaller TheChosenDownloader-Full.spec -y  # 267MB, includes playwright

# Create DMG
create-dmg --volname "The Chosen Downloader" \
  --app-drop-link 600 185 \
  "dist/The-Chosen-Downloader.dmg" \
  "dist/TheChosenDownloader.app"
```

See `docs/BUILD.md` for detailed build documentation.

## PyInstaller Notes

- Uses **onedir mode** for fast startup (~2s vs 10s+ with onefile)
- GUI-only bundle: ~136MB (excludes playwright, lxml, bs4)
- Full bundle: ~267MB (includes playwright for CLI URL extraction)
- Key spec settings:
  - `exclude_binaries=True` in EXE
  - COLLECT step gathers all files
  - BUNDLE wraps COLLECT (not EXE directly)
  - Info.plist: `LSBackgroundOnly: False`, `LSUIElement: False`

## Bundled App Behavior

When running as bundled .app (`sys.frozen` is set):
- Defaults to GUI mode (no args needed)
- Data files in `sys._MEIPASS` directory
- Splash window shown before heavy imports (keeps dock icon visible)

## Common Issues

| Issue | Solution |
|-------|----------|
| Dock icon disappears | Use onedir mode, check Info.plist settings |
| season1.json not found | Check `sys._MEIPASS` path in code |
| Slow startup (10s+) | Switch from onefile to onedir mode |
| Module not found | Add to `hiddenimports` in spec |