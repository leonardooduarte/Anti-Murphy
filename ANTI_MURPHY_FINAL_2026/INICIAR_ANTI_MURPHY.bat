@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 start.py
) else (
  where python >nul 2>&1
  if not errorlevel 1 (
    python start.py
  ) else (
    echo Python 3.10 ou superior nao encontrado. Instale Python e execute novamente.
    pause
    exit /b 1
  )
)
if errorlevel 1 (
  echo O programa foi encerrado com erro. Confira a mensagem acima.
  pause
)
