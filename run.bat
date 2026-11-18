@echo off
REM Orion capstone - one-click run on Windows
REM   run.bat          full run (all tests)
REM   run.bat smoke    smoke tests only
if not exist .venv (
  py -3 -m venv .venv || python -m venv .venv
)
call .venv\Scripts\activate
if exist wheels (
  python -m pip install -q --no-index --find-links wheels -r requirements.txt || exit /b 1
) else (
  python -m pip install -q -r requirements.txt || exit /b 1
)
python pipeline\run_pipeline.py || exit /b 1
if "%1"=="smoke" (
  pytest -m smoke --html=reports\report.html --self-contained-html
) else (
  pytest -rs --html=reports\report.html --self-contained-html
)
echo.
echo Report: reports\report.html   Evidence: reports\evidence\
