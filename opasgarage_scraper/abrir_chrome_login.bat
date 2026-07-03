@echo off
REM ============================================================
REM  Abre o Google Chrome com depuracao ligada (porta 9222)
REM  para o scraper conseguir se conectar a sessao ja logada.
REM
REM  COMO USAR:
REM   1) Feche TODAS as janelas do Chrome antes de rodar isto.
REM   2) De dois cliques neste arquivo (ou rode no PowerShell:
REM        .\abrir_chrome_login.bat  )
REM   3) Na janela do Chrome que abrir, faca login no Opas Garage
REM      (com o Google, normal). DEIXE a janela aberta.
REM   4) Volte ao PowerShell e rode:  python scraper.py all
REM ============================================================

set "PROFILE=%~dp0chrome-profile"

REM Tenta os locais mais comuns de instalacao do Chrome.
set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"

if not exist "%CHROME%" (
  echo Nao encontrei o Chrome nos locais padrao.
  echo Edite este arquivo e coloque o caminho do seu chrome.exe na variavel CHROME.
  pause
  exit /b 1
)

echo Abrindo o Chrome com depuracao na porta 9222...
echo Faca login no Opas Garage na janela que abrir e DEIXE aberta.
start "" "%CHROME%" --remote-debugging-port=9222 --user-data-dir="%PROFILE%"
