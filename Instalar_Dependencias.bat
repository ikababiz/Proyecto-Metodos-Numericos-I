@echo off
echo ====================================================
echo Instalando dependencias (MiKTeX) para el proyecto...
echo ====================================================

echo.
echo 1. Descargando e instalando MiKTeX (~142MB, esto puede tardar unos minutos)...
winget install --id MiKTeX.MiKTeX --silent --accept-source-agreements --accept-package-agreements

echo.
echo 2. Configurando "Install missing packages on-the-fly" a "Yes"...
set PATH=%PATH%;%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64;%ProgramFiles%\MiKTeX\miktex\bin\x64

initexmf --set-config-value=[Core]AutoInstall=1

echo.
echo ====================================
echo Ya puedes ejecutar MenuPrincipal.exe
echo ====================================
pause