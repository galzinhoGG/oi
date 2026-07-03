@echo off
REM ============================================================
REM  PASSO 2 de 2 - Abre o Chrome COM depuracao (porta 9222),
REM  reusando o perfil onde voce JA logou no PASSO 1.
REM
REM  IMPORTANTE: rode o PASSO 1 (passo1_logar.bat) e feche o
REM  Chrome antes. Aqui voce NAO precisa logar de novo - a
REM  sessao ja esta salva. (O Google bloqueia login com a
REM  depuracao ligada; por isso o login e feito no passo 1.)
REM
REM  COMO USAR:
REM   1) Ja fez o PASSO 1 e fechou o Chrome? Entao siga.
REM   2) De dois cliques neste arquivo.
REM   3) O Opas Garage deve abrir JA LOGADO. DEIXE a janela aberta.
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

echo Abrindo o Chrome com depuracao na porta 9222 (ja deve estar logado)...
echo DEIXE a janela aberta e rode no PowerShell:  python scraper.py all
start "" "%CHROME%" --remote-debugging-port=9222 --user-data-dir="%PROFILE%" "https://opasgarage.com.br"
