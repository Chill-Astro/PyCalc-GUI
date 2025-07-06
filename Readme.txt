To export using Pyinstaller,

pyinstaller -F -i PyCalc-GUI.ico --add-data "Inter.ttf;." --add-data "icomoon.ttf;." --add-data "PyCalc-GUIico;." PyCalc-GUI.py --noconsole

[ If without icon ]

pyinstaller -F --add-data "Inter.ttf;." --add-data "icomoon.ttf;." --add-data "PyCalc-GUIico;." PyCalc-GUI.py --noconsole

If Pyinstaller not available,

pip install pyinstaller

Other Pyinstaller Alternatives can also be used.