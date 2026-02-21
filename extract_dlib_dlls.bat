@echo off
echo Extracting dlib DLL files...

:: Run the Python script
"%LOCALAPPDATA%\Programs\Python\Python313\python.exe" "%~dp0extract_dlib_dlls.py"

echo.
echo If the script ran successfully, try importing dlib again.
echo If you still encounter issues, follow the instructions provided by the script.

pause