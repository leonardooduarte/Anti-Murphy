@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
if "%~1"=="" (
  echo Arraste a pasta ANTI_MURPHY_FINAL_2026 recem-extraida sobre este arquivo BAT.
  echo O diagnostico usa uma copia temporaria e preserva a pasta original.
  pause
  exit /b 1
)
where py >nul 2>&1
if not errorlevel 1 (
  py -3 "%~dp0VERIFICAR_AMBIENTE.py" --app "%~1"
) else (
  python "%~dp0VERIFICAR_AMBIENTE.py" --app "%~1"
)
echo.
echo O JSON de resultado fica nesta pasta. O ensaio visual e no projetor continua manual.
pause
