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
        self.sub_ui.exportButton.clicked.connect(self.exportToExcel)
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

    def getMatrix(self) -> np.ndarray:
        rows = self.table.rowCount()
        cols = self.table.columnCount()
        matrix = np.zeros([rows, cols])
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
        # X = self.getMatrix()
        # l = np.shape(X)[0]  # Чмсло вариантов
        # n = np.shape(X)[1]  # Число наблюдений
        # V = np.sum(X, axis=1)  # Суммы
        # N = np.size(X)  # Общее число наблюдений
        # avg = np.average(X)
        #
        # C = pow(np.sum(X), 2) / N
        # CY = np.sum(np.square(X)) - C
        # CV = np.sum(np.square(V)) / n - C
        # CZ = CY - CV
        # s2v = CV / (l - 1)  # средний квадрат вариантов
        # s2 = CZ / (N - l)  # средний кадрат ошибки
        # v = 100 * math.sqrt(s2) / avg  # коэффициент вариации, %
        #
        # sx = math.sqrt(s2 / n)  # ошибка оптыта
        # sd = math.sqrt(2 * s2 / n)  # ошибка разности средних
        # sd_percent = 100 * sd / avg  # относительная ошибка разницы средних
        #
        # Ff = s2v / s2
        # F05 = ft.f05_distr(n, N - l)
        # t05 = ft.t_crit(0.95, N - l)
        #
        # HCP05 = t05 * sd
        # HCP05_percent = (HCP05 * 100) / avg
        disp = DispOutput(self.getMatrix())
        return disp

    def exportToExcel(self):
        disp = self.calculate()
        disp.roundVals(2)
        disp.toExcel()

    def showResults(self):
        disp = self.calculate()
        disp.roundVals(2)
        self.sub_window.show()
        self.sub_ui.textEdit.setText(disp.toMarkdown())
        self.save_configs()


class DispOutput:
    def __init__(self, X):
        self.X: np.ndarray = X

        self.l: int = np.shape(X)[0]  # Чмсло вариантов
        self.n: int = np.shape(X)[1]  # Число наблюдений
        self.N: int = np.size(X)  # Общее число наблюдений
        self.V = np.sum(X, axis=1)  # Суммы
        self.avg: float = np.average(X)

        self.C: float = pow(np.sum(X), 2) / self.N
        self.CY: float = np.sum(np.square(X)) - self.C
        self.CV: float = np.sum(np.square(self.V)) / self.n - self.C
        self.CZ: float = self.CY - self.CV
        self.s2v: float = self.CV / (self.l - 1)  # средний квадрат вариантов
        self.s2: float = self.CZ / (self.N - self.l)  # средний кадрат ошибки
        self.v: float = 100 * math.sqrt(self.s2) / self.avg  # коэффициент вариации, %

        self.sx: float = math.sqrt(self.s2 / self.n)  # ошибка оптыта
        self.sd: float = math.sqrt(2 * self.s2 / self.n)  # ошибка разности средних
        self.sd_percent: float = 100 * self.sd / self.avg  # относительная ошибка разницы средних

        self.Ff: float = self.s2v / self.s2
        self.F05: float = ft.f05_distr(self.n, self.N - self.l)
        self.t05: float = ft.t_crit(0.95, self.N - self.l)

        self.HCP05: float = self.t05 * self.sd
        self.HCP05_percent: float = (self.HCP05 * 100) / self.avg

    def roundVals(self, n):
        self.CY = round(self.CY, n)
        self.CV = round(self.CV, n)
        self.CZ = round(self.CZ, n)
        self.s2 = round(self.s2, n)
        self.s2v = round(self.s2v, n)
        self.sx = round(self.sx, n)
        self.sd = round(self.sd, n)
        self.sd_percent = round(self.sd_percent, n)
        self.Ff = round(self.Ff, n)
        self.F05 = round(self.F05, n)
        self.v = round(self.v, n)
        self.HCP05 = round(self.HCP05, n)
        self.HCP05_percent = round(self.HCP05_percent, n)

    def toMarkdown(self) -> str:
        text = 'Вхідні дані\n'
        columns = ['Варіанти']
        for i in range(0, self.n):
            columns.append(str(i + 1))
        columns.append('К-ть\nспост.')
        columns.append('Суми')
        columns.append('Середні')
        body = []
        for i in range(0, self.l):
            row = list(self.X[i])
            row.insert(0, str(i + 1))
            row.append(self.n)
            row.append(self.V[i])
            row.append(np.average(self.X, axis=1)[i])
            body.append(row)
        table = pd.DataFrame(body, columns=columns)
        text += table.to_markdown(index=False,
                                  tablefmt='fancy_grid',
                                  floatfmt=".2f",
                                  stralign="center",
                                  numalign='center')
        text += f'\n\nЗагальна кількіть спостережень: {self.N}'
        text += f'\nЗагальна сума: {round(self.V.sum(), 2)}'
        text += f'\nСереднє по досліду: {self.avg}'

        columns = ['Дисперсія', 'Сума\nквадратів', 'Ступені\nсвободи', 'Середній\nквадрат', 'Fф', 'F05']
        body = [['Загальна', self.CY, self.N - 1, '--', '--', '--'],
                ['Варіантів', self.CV, self.l - 1, self.s2v, self.Ff, self.F05],
                ['Залишок (помилки)', self.CZ, self.N - self.l, self.s2, '--', '--']]
        table = pd.DataFrame(body, columns=columns)

        text += '\n\nРезультати дисперсійного аналізу\n'
        text += table.to_markdown(index=False,
                                  tablefmt='fancy_grid',
                                  floatfmt=".2f",
                                  stralign="center",
                                  numalign='center')

        text += '\n\n'
        text += f'Критерій суттєвості: {self.Ff}\n'
        text += f'Критерій F на 5%-му рівні значимості: {self.F05}\n'
        text += f'Помилка досліду: {self.sx}\n'
        text += f'Помилка різниці середніх: {self.sd}\n'
        text += f'Відносна помилка різниці середніх: {self.sd_percent}%\n'
        text += f'Коефіцієнт варіації: {self.v}%\n'
        text += f'НІР абсолютне: {self.HCP05}\n'
        text += f'НІР відносне: {self.HCP05_percent}%'

        return text

    def toExcel(self):
        columns = ['Варіанти']
        for i in range(0, self.n):
            columns.append(str(i + 1))
        columns.append('К-ть\nспост.')
        columns.append('Суми')
        columns.append('Середні')
        body = []
        for i in range(0, self.l):
            row = list(self.X[i])
            row.insert(0, str(i + 1))
            row.append(self.n)
            row.append(self.V[i])
            row.append(np.average(self.X, axis=1)[i])
            body.append(row)
        table_01 = pd.DataFrame(body, columns=columns)

        head = ['Дисперсія', 'Сума\nквадратів', 'Ступені\nсвободи', 'Середній\nквадрат', 'Fф', 'F05']
        body = [['Загальна', self.CY, self.N - 1, '--', '--', '--'],
                ['Варіантів', self.CV, self.l - 1, self.s2v, self.Ff, self.F05],
                ['Залишок (помилки)', self.CZ, self.N - self.l, self.s2, '--', '--']]
        table_02 = pd.DataFrame(body, columns=head)

        writer = pd.ExcelWriter("result.xlsx", engine='xlsxwriter')
        table_01.to_excel(writer, sheet_name='Sheet1', index=False, startrow=0)
        table_02.to_excel(writer, sheet_name='Sheet1', index=False, startrow=self.n + 5)

        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        format_cells = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        format_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'font_size': 10})
        worksheet.set_column(0, 0, 18, format_cells)
        worksheet.set_column(2, 99, None, format_cells)

        worksheet.merge_range(self.l + 1, 0, self.l + 1, self.n, 'Загальна сума', format_right)
        worksheet.write(self.l + 1, self.n + 1, self.N, format_cells)
        worksheet.write(self.l + 1, self.n + 2, round(self.V.sum(), 2), format_cells)
        worksheet.write(self.l + 1, self.n + 3, self.avg, format_cells)

        worksheet.merge_range(self.l + 10, 0, self.l + 10, self.n, 'Критерій суттєвості', format_right)
        worksheet.write(self.l + 10, self.n + 1, self.Ff, format_cells)
        worksheet.merge_range(self.l + 11, 0, self.l + 11, self.n, 'Критерій F на 5%-му рівні значимості', format_right)
        worksheet.write(self.l + 11, self.n + 1, self.F05, format_cells)
        worksheet.merge_range(self.l + 12, 0, self.l + 12, self.n, 'Помилка досліду', format_right)
        worksheet.write(self.l + 12, self.n + 1, self.sx, format_cells)
        worksheet.merge_range(self.l + 13, 0, self.l + 13, self.n, 'Помилка різниці середніх', format_right)
        worksheet.write(self.l + 13, self.n + 1, self.sd, format_cells)
        worksheet.merge_range(self.l + 14, 0, self.l + 14, self.n, 'Відносна помилка різниці середніх (%)', format_right)
        worksheet.write(self.l + 14, self.n + 1, self.sd_percent, format_cells)
        worksheet.merge_range(self.l + 15, 0, self.l + 15, self.n, 'Коефіцієнт варіації', format_right)
        worksheet.write(self.l + 15, self.n + 1, self.v, format_cells)
        worksheet.merge_range(self.l + 16, 0, self.l + 16, self.n, 'НІР абсолютне', format_right)
        worksheet.write(self.l + 16, self.n + 1, self.HCP05, format_cells)
        worksheet.merge_range(self.l + 17, 0, self.l + 17, self.n, 'НІР відносне (%)', format_right)
        worksheet.write(self.l + 17, self.n + 1, self.HCP05_percent, format_cells)

        writer.save()


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())


main()






