#!/bin/bash
# Run the GUI for manual testing

cd "$(dirname "$0")"
.venv/bin/python -c "from thechosen_downloader.gui import main; main()"
