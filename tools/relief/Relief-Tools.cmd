@echo off
rem Double-click launcher for Fix-Machine.ps1 in this folder.
cd /d "%~dp0"
where pwsh >nul 2>nul
if errorlevel 1 goto nopwsh
set "PS=pwsh -NoProfile -ExecutionPolicy Bypass -File"

:menu
cls
echo.
echo   MACHINE RELIEF   (C: space, page file, Claude sessions)
echo   ------------------------------------------------------------
echo   1  Scan                                  (changes nothing)
echo   2  Dry run: what each stage would free   (changes nothing)
echo   3  Fix until unblocked                   (asks before each stage)
echo   4  Fix all stages, then offer a restart  (asks)
echo   5  Run one stage: temp / pkgcache / fsmonitor / onedrive / sessions
echo   6  Watch every 5 min                     (beeps when blocked; Ctrl+C stops)
echo   7  Install the "relief" command in PowerShell
echo   Q  Quit
echo.
set "c="
set /p "c=  Choose 1-7 or Q: "
if /i "%c%"=="q" exit /b 0
if "%c%"=="1" %PS% "%~dp0Fix-Machine.ps1" -ListOnly
if "%c%"=="2" %PS% "%~dp0Fix-Machine.ps1" -DryRun
if "%c%"=="3" %PS% "%~dp0Fix-Machine.ps1"
if "%c%"=="4" %PS% "%~dp0Fix-Machine.ps1" -All -Reboot
if "%c%"=="5" goto one
if "%c%"=="6" %PS% "%~dp0Fix-Machine.ps1" -Watch 300
if "%c%"=="7" %PS% "%~dp0Fix-Machine.ps1" -InstallAlias
goto done

:one
set "s="
set /p "s=  Stage (temp, pkgcache, fsmonitor, onedrive, sessions): "
if not defined s goto menu
%PS% "%~dp0Fix-Machine.ps1" -Stage %s%
goto done

:done
echo.
pause
goto menu

:nopwsh
echo PowerShell 7 (pwsh) was not found. Install it with:  winget install Microsoft.PowerShell
pause
exit /b 1
