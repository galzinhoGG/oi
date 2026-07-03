@echo off
REM ============================================================
REM  PASSO 1 de 2 - LOGAR (Chrome normal, SEM depuracao)
REM
REM  O Google bloqueia login quando a depuracao esta ligada.
REM  Entao aqui abrimos o Chrome NORMAL (o Google aceita), voce
REM  loga, e a sessao fica salva no perfil. Depois o PASSO 2
REM  reabre o MESMO perfil com depuracao, ja logado.
REM
REM  COMO USAR:
REM   1) Feche TODAS as janelas do Chrome antes.
REM   2) De dois cliques neste arquivo.
REM   3) Faca login no Opas Garage com o Google na janela que abrir.
REM   4) Confirme que esta logado e FECHE o Chrome COMPLETAMENTE
REM      (feche todas as janelas do Chrome).
REM   5) Agora rode o PASSO 2:  abrir_chrome_login.bat
REM ============================================================

set "PROFILE=%~dp0chrome-profile"

set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"

if not exist "%CHROME%" (
  echo Nao encontrei o Chrome. Edite este arquivo e ajuste a variavel CHROME.
  pause
  exit /b 1
)

echo ============================================================
echo  PASSO 1: Faca login no Opas Garage (com o Google) na janela
echo  que vai abrir. Depois de logado, FECHE o Chrome por completo
echo  e rode o PASSO 2 (abrir_chrome_login.bat).
echo ============================================================
start "" "%CHROME%" --user-data-dir="%PROFILE%" "https://opasgarage.com.br"
