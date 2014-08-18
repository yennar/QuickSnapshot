@echo off
upx dist\*.exe
upx dist\*.dll
cd dist
7z a archive.7z *.exe *.dll
cd ..
copy /b 7zS.sfx + config.txt + dist\archive.7z ..\QuickCapture.exe