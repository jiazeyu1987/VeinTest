@echo off
set LRELEASE_PATH=D:/Slicer540/bin/lrelease.exe
set TS_FILE=zh_zh-CN.ts
set QM_FILE=D:\S521\S4R\Slicer-build\bin\translations\zh_zh-CN.qm

REM Step 1: Compile the .ts file
"%LRELEASE_PATH%" "%TS_FILE%"

@pause