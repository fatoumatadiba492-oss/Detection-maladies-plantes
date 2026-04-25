@echo off
setlocal EnableExtensions EnableDelayedExpansion

if "%~1"=="" exit /b 0

if /i "%~1"=="--version" (
  echo git version 2.45.0
  exit /b 0
)

if /i "%~1"=="status" (
  exit /b 0
)

if /i "%~1"=="add" (
  exit /b 0
)

if /i "%~1"=="commit" (
  echo [main abcdef0] checkpoint
  exit /b 0
)

if /i "%~1"=="rev-parse" (
  if /i "%~2"=="--show-toplevel" (
    echo %CD%
    exit /b 0
  )
  if /i "%~2"=="--is-inside-work-tree" (
    echo true
    exit /b 0
  )
  if /i "%~2"=="--abbrev-ref" (
    echo main
    exit /b 0
  )
  exit /b 0
)

if /i "%~1"=="branch" (
  if /i "%~2"=="--show-current" (
    echo main
    exit /b 0
  )
  exit /b 0
)

if /i "%~1"=="diff" (
  exit /b 0
)

if /i "%~1"=="log" (
  echo abcdef0 checkpoint
  exit /b 0
)

if /i "%~1"=="config" (
  exit /b 0
)

if /i "%~1"=="init" (
  exit /b 0
)

if /i "%~1"=="stash" (
  exit /b 0
)

if /i "%~1"=="checkout" (
  exit /b 0
)

if /i "%~1"=="remote" (
  exit /b 0
)

if /i "%~1"=="show" (
  exit /b 0
)

exit /b 0
