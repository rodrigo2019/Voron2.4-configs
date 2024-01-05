#!/usr/bin/env bash

source ~/maintenance_tracker-env/bin/activate
python ~/printer_data/config/maintenance_tracker/reset_db.py "$@"
deactivate
