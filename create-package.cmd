@ECHO OFF

SET FILE_NAME=da-Websocket-Client

IF NOT EXIST "bin" (
  ECHO ERROR: Missing 'bin' folder. See the instruction to build project first.
  GOTO L_EXIT
)

ECHO Creating .zip package ...

XCOPY /Y /E preferences\* bin\preferences\

SET PATH=%PATH%;C:\Program Files\WinRAR;C:\Program Files (x86)\WinRAR
WinRAR a -afzip -r "bin.zip" "bin"

ECHO Finished

:L_EXIT
PAUSE