from distutils.core import setup
import py2exe
import sys
 
#this allows to run it with a simple double click.
sys.argv.append('py2exe')


py2exe_options = {
        "dll_excludes": ["MSVCP90.dll","w9xpopen.exe"],
        "compressed": 1,
        "optimize": 2,
        "ascii": 0,
        "includes": ["sip","PyQt4.QtCore","PyQt4.QtGui","pygs","ctypes"],
        "bundle_files": 1,
        }
 
setup(
      name = 'QuickCapture',
      version = '1.0',
      windows = [{
            'script' : 'QuickCapture.py'
             },
           ],     
      zipfile = None,
      options = {'py2exe': py2exe_options},
      data_files=[('.',['QxtGlobalShortcut.dll'])]
      )