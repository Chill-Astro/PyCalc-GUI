To export using Pyinstaller,

pyinstaller -F -i PyC_GUI.ico --add-data "Inter.ttf;." --add-data "icomoon.ttf;." --add-data "PyC_GUI.ico;." PyC_GUI.py --noconsole

If without icon,

pyinstaller -F --add-data "Inter.ttf;." --add-data "icomoon.ttf;." --add-data "PyC_GUI.ico;." PyC_GUI.py --noconsole

If Pyinstaller not available,

pip install pyinstaller