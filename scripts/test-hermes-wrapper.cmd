@echo off
echo Running Hermes wrapper manual verification...
python scripts/tests/test_hermes_control.py
echo Done. Exit code: %ERRORLEVEL%
