@echo off
echo This script is used to build the executable file.
pyinstaller --name UeTool.exe --workpath ..\build --distpath ..\binaries  --specpath ..\build --noconsole --onefile ..\main.py

copy  ..\build\UeTool.exe H:\Sync\Scripts\Windows\04_tools\UeTool.exe /Y
echo Done!
echo The executable file has been copied to H:\Sync\Scripts\Windows\04_tools\
pause
```
