# Опис
Програма для розрахунку дисперсійного аналізу.

# Build
pyinstaller -F -w --paths=venv\Lib\site-packages --hidden-import=tabulate --name "dispersion" main.py
for building for Windows 7 you'll need python 3.8 and pyQt5

# Misc
.gitignore generated from https://www.toptal.com/developers/gitignore