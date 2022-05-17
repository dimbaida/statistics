import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow
from ui.main_window import Ui_MainWindow
from ui.result import Ui_SubWindow

import math
import numpy as np
import json
import pandas as pd
from pathlib import Path

import fisher_tables as ft


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.cols.valueChanged.connect(self.updateTable)
        self.rows.valueChanged.connect(self.updateTable)

        # Sub Window
        self.sub_window = QtWidgets.QMainWindow()
        self.sub_ui = Ui_SubWindow()
        self.sub_ui.setupUi(self.sub_window)
        # Button Event
        self.pushButton.clicked.connect(self.showResults)

        self.load_configs()

    def updateTable(self):
        _translate = QtCore.QCoreApplication.translate
        col = self.cols.value()
        row = self.rows.value()
        self.table.setColumnCount(col)
        self.table.setRowCount(row)
        self.updateTableSize()
        for i in range(0, col):
            item = QtWidgets.QTableWidgetItem()
            item.setText(f'повт {i + 1}')
            self.table.setHorizontalHeaderItem(i, item)
        for i in range(0, row):
            item = QtWidgets.QTableWidgetItem()
            item.setText(f'вар {i + 1}')
            self.table.setVerticalHeaderItem(i, item)

    def updateTableSize(self):
        col = self.cols.value()
        row = self.rows.value()
        self.table.setFixedSize(45 + col * 50, 25 + row * 23)
        self.resize(90 + col * 50, 180 + row * 23)

    def save_configs(self):
        cfg_path = Path.home() / Path('.variance-analysis-cfg')
        cfg = {'rows': self.rows.value(),
               'cols': self.cols.value(),
               'cells': self.getMatrix().round(2).tolist()
               }
        with open(cfg_path, 'w') as f:
            json_string = json.dumps(cfg, default=lambda o: o.__dict__, sort_keys=True, indent=2)
            f.write(json_string)

    def load_configs(self):
        cfg_path = Path.home() / Path('.variance-analysis-cfg')
        if cfg_path.exists():
            with open(cfg_path) as json_file:
                cfg = json.load(json_file)
            try:
                self.rows.setValue(cfg['rows'])
            except KeyError as e:
                print("Missing attribute in .cfg file:", e)
            try:
                self.cols.setValue(cfg['cols'])
            except KeyError as e:
                print("Missing attribute in .cfg file:", e)
            try:
                values = cfg['cells']
                self.writeCells(values)
            except KeyError as e:
                print("Missing attribute in .cfg file:", e)
        self.updateTableSize()

    def getMatrix(self):
        rows = self.table.rowCount()
        cols = self.table.columnCount()
        matrix = np.empty([rows, cols])
        for col in range(0, self.table.columnCount()):
            for row in range(0, self.table.rowCount()):
                item = self.table.item(row, col)
                if item:
                    matrix[row, col] = float(item.text().replace(',', '.'))
        return matrix

    def writeCells(self, data: list):
        rows = self.table.rowCount()
        cols = self.table.columnCount()
        for row in range(0, rows):
            for col in range(0, cols):
                text = str(data[row][col])
                item = QtWidgets.QTableWidgetItem()
                item.setText(text)
                self.table.setItem(row, col, item)

    def calculate(self):
        X = self.getMatrix()
        l = np.shape(X)[0]  # Чмсло вариантов
        n = np.shape(X)[1]  # Число наблюдений
        V = np.sum(X, axis=1)  # Суммы
        N = np.size(X)  # Общее число наблюдений
        avg = np.average(X)

        C = pow(np.sum(X), 2) / N
        CY = np.sum(np.square(X)) - C
        CV = np.sum(np.square(V)) / n - C
        CZ = CY - CV
        s2v = CV / (l - 1)  # средний квадрат вариантов
        s2 = CZ / (N - l)  # средний кадрат ошибки
        v = 100 * math.sqrt(s2) / avg  # коэффициент вариации, %

        sx = math.sqrt(s2 / n)  # ошибка оптыта
        sd = math.sqrt(2 * s2 / n)  # ошибка разности средних
        sd_percent = 100 * sd / avg  # относительная ошибка разницы средних

        Ff = s2v / s2
        F05 = ft.f05_distr(n, N - l)
        t05 = ft.t_crit(0.95, N - l)

        HCP05 = t05 * sd
        HCP05_percent = (HCP05 * 100) / avg

        CY = round(CY, 2)
        CV = round(CV, 2)
        s2 = round(s2, 2)
        s2v = round(s2v, 2)
        sx = round(sx, 2)
        sd = round(sd, 2)
        sd_percent = round(sd_percent, 2)
        Ff = round(Ff, 2)
        F05 = round(F05, 2)
        v = round(v, 2)
        HCP05 = round(HCP05, 2)
        HCP05_percent = round(HCP05_percent, 2)

        output_table = [['Загальна', CY, N - 1, '--', '--', '--'],
                        ['Варіантів', CV, l - 1, s2v, Ff, F05],
                        ['Залишок (помилки)', CZ, N - l, s2, '--', '--']]
        columns = ['Дисперсія', 'Сума\nквадратів', 'Ступені\nсвободи', 'Середній\nквадрат', 'Fф', 'F05']
        table = pd.DataFrame(output_table, columns=columns)

        # text = table.to_html(index=False, decimal=',', classes='table table-stripped')
        text = table.to_markdown(index=False, tablefmt='fancy_grid', floatfmt=".2f", stralign="center", numalign='center')

        text += '\n\n\n'
        text += f'Критерій суттєвості = {Ff}\n'
        text += f'Критерій F на 5%-му рівні значимості = {F05}\n'
        text += f'Помилка досліду = {sx}\n'
        text += f'Помилка різниці середніх = {sd}\n'
        text += f'Відносна помилка різниці середніх = {sd_percent}%\n'
        text += f'Коефіцієнт варіації = {v}%\n'
        text += f'НІР абсолютне = {HCP05}\n'
        text += f'НІР відносне = {HCP05_percent}%'

        return text

    def showResults(self):
        text = self.calculate()
        self.sub_window.show()
        self.sub_ui.textEdit.setText(text)
        self.save_configs()


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())


main()






