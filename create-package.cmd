@ECHO OFF

SET PATH=%PATH%;C:\Program Files\WinRAR;C:\Program Files (x86)\WinRAR

IF EXIST "bin" (
  ECHO Creating package ...
  XCOPY /Y /E preferences\* bin\preferences\
  XCOPY /Y /E plugins\* bin\plugins\
  WinRAR a -afzip -r "bin.zip" "bin"
  ECHO Finished
) ELSE (
  ECHO ERROR: Missing 'bin' folder. See the instruction to build project first.
)

PAUSE