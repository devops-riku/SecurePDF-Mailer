@echo off
title Building SecurePDF Mailer (Nuitka)

REM =========================
REM  APP INFO
REM =========================
set APP_NAME=SecurePDF Mailer - rikucat
set ICON=icon.ico

REM =========================
REM  CLEAN OLD BUILDS
REM =========================
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

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
    --include-package=msal ^
    --include-package=msal_extensions ^
    --include-package=requests ^
    --include-package=base64 ^
    --include-package=re ^
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
