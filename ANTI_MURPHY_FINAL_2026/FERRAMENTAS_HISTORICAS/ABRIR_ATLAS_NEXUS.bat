@echo off
setlocal
cd /d "%~dp0.."
set "PYTHONUTF8=1"
if not exist ".venv_classic\Scripts\python.exe" (
  echo Preparando o ambiente das ferramentas historicas (apenas na primeira execucao)...
  where py >nul 2>&1
  if errorlevel 1 (echo Python nao encontrado.&pause&exit /b 1)
  py -3 -m venv .venv_classic
  if errorlevel 1 (echo Falha ao criar o ambiente Python.&pause&exit /b 1)
  ".venv_classic\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 (echo Falha ao instalar as ferramentas historicas.&pause&exit /b 1)
)
echo Abrindo interface classica do Anti-Murphy...
".venv_classic\Scripts\python.exe" -m streamlit run app.py --server.port 8501
if errorlevel 1 pause
