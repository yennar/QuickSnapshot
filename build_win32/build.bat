@echo off
copy ../src/*.py .
mkdir res
copy ../src/res/* ./res/
python build_exe.py
upx dist\QuickSnapshot.exe
