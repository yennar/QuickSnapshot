@echo off
copy ..\src\*.py .
mkdir res
copy ..\src\res\* .\res\
python build_exe.py
upx dist\QuickCapture.exe
cd dist
del Qt*.dll
7z a archive.7z *.exe *.dll
cd ..
copy /b 7zS.sfx + config.txt + dist\archive.7z ..\QuickCapture.exe
