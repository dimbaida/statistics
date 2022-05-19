Если требуется запустить под mac, нужно обнопить интерпретатор до python 3.10 и модуль PyQt6

# To Build
pyinstaller -F -w --paths=venv\Lib\site-packages --hidden-import=tabulate --name "dispersion" main.py