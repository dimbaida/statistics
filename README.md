
# To Build
pyinstaller -F -w --paths=venv\Lib\site-packages --hidden-import=tabulate --name "dispersion" main.py