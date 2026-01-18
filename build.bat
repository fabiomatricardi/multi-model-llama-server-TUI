@echo off
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Building TUI-CPP standalone executable...
pyinstaller TUI-CPP.spec

echo.
echo Build complete! Executable located in: dist\TUI-CPP.exe
echo.
echo Make sure to place llama-server.exe and models/ folder next to TUI-CPP.exe
pause
