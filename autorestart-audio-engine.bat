:start

py autorestart-audio-engine.py

:: Restart if the python script exited cleanly and was not killed
IF %ERRORLEVEL% EQU 0 (
    timeout 5
    goto start
)
