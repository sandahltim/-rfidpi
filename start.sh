#!/bin/bash
source venv/bin/activate
gunicorn --workers 2 --bind 0.0.0.0:8101 run:app
