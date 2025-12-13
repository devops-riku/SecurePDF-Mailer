@echo off
title Building SecurePDF Mailer (Nuitka)

REM =========================
REM  APP INFO
REM =========================
set APP_NAME="SecurePDF Mailer - rikucat"
set ICON=icon.ico   REM <-- your icon file

REM =========================
REM  BUILD WITH NUITKA
REM =========================
python -m nuitka ^
    --standalone ^
    --onefile ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=icon.ico ^
    --enable-plugin=pyside6 ^
    --include-data-dir=config=config ^
    --include-package=core ^
    --include-package=ui ^
    --include-package=pythoncom ^
    --include-package=win32com ^
    --follow-imports ^
    --output-dir=dist ^
    main.py

echo.
echo ====================================
echo       BUILD COMPLETED SUCCESSFULLY!
echo.
echo   OUTPUT → dist\main.exe
echo   Rename to → SecurePDF Mailer.exe
echo ====================================
pause
