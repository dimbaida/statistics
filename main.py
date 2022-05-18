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
        # TODO: update min size

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

    def calculate(self):  # TODO: add preliminary tables
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

        output = Output()
        output.N = N
        output.l = l
        output.CY = CY
        output.CV = CV
        output.CZ = CZ
        output.s2 = s2
        output.s2v = s2v
        output.sx = sx
        output.sd = sd
        output.sd_percent = sd_percent
        output.Ff = Ff
        output.F05 = F05
        output.v = v
        output.HCP05 = HCP05
        output.HCP05_percent = HCP05_percent

        return output

    def exportToExcel(self):
        output = self.calculate()
        output.roundValues(2)
        output.toExcel()

    def showResults(self):
        output = self.calculate()
        output.roundValues(2)
        self.sub_window.show()
        self.sub_ui.textEdit.setText(output.toMarkdown())
        self.save_configs()


class Output:
    def __init__(self):
        self.N: int | None = None
        self.l: int | None = None
        self.CY: float | None = None
        self.CV: float | None = None
        self.CZ: float | None = None
        self.s2: float | None = None
        self.s2v: float | None = None
        self.sx: float | None = None
        self.sd: float | None = None
        self.sd_percent: float | None = None
        self.Ff: float | None = None
        self.F05: float | None = None
        self.v: float | None = None
        self.HCP05: float | None = None
        self.HCP05_percent: float | None = None

    def roundValues(self, n):
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
        output_table = [['Загальна', self.CY, self.N - 1, '--', '--', '--'],
                        ['Варіантів', self.CV, self.l - 1, self.s2v, self.Ff, self.F05],
                        ['Залишок (помилки)', self.CZ, self.N - self.l, self.s2, '--', '--']]
        columns = ['Дисперсія', 'Сума\nквадратів', 'Ступені\nсвободи', 'Середній\nквадрат', 'Fф', 'F05']
        table = pd.DataFrame(output_table, columns=columns)

        text = table.to_markdown(index=False,
                                 tablefmt='fancy_grid',
                                 floatfmt=".2f",
                                 stralign="center",
                                 numalign='center')

        text += '\n\n'
        text += f'Критерій суттєвості = {self.Ff}\n'
        text += f'Критерій F на 5%-му рівні значимості = {self.F05}\n'
        text += f'Помилка досліду = {self.sx}\n'
        text += f'Помилка різниці середніх = {self.sd}\n'
        text += f'Відносна помилка різниці середніх = {self.sd_percent}%\n'
        text += f'Коефіцієнт варіації = {self.v}%\n'
        text += f'НІР абсолютне = {self.HCP05}\n'
        text += f'НІР відносне = {self.HCP05_percent}%'

        return text

    def toExcel(self):
        head = ['Дисперсія', 'Сума\nквадратів', 'Ступені\nсвободи', 'Середній\nквадрат', 'Fф', 'F05']
        body = [['Загальна', self.CY, self.N - 1, '--', '--', '--'],
                ['Варіантів', self.CV, self.l - 1, self.s2v, self.Ff, self.F05],
                ['Залишок (помилки)', self.CZ, self.N - self.l, self.s2, '--', '--']]
        table = pd.DataFrame(body, columns=head)
        
        writer = pd.ExcelWriter("result.xlsx", engine='xlsxwriter')
        table.to_excel(writer, sheet_name='Sheet1', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        format_cells = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        format_text = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'font_size': 10})
        worksheet.set_column(0, 0, 18, format_cells)
        worksheet.set_column(1, 1, 12, format_cells)
        worksheet.set_column(2, 6, None, format_cells)

        worksheet.write('A6', f'Критерій суттєвості = {self.Ff}', format_text)
        worksheet.write('A7', f'Критерій F на 5%-му рівні значимості = {self.F05}', format_text)
        worksheet.write('A8', f'Помилка досліду = {self.sx}', format_text)
        worksheet.write('A9', f'Помилка різниці середніх = {self.sd}', format_text)
        worksheet.write('A10', f'Відносна помилка різниці середніх = {self.sd_percent}%', format_text)
        worksheet.write('A11', f'Коефіцієнт варіації = {self.v}%', format_text)
        worksheet.write('A12', f'НІР абсолютне = {self.HCP05}', format_text)
        worksheet.write('A13', f'НІР відносне = {self.HCP05_percent}%', format_text)

        writer.save()


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())


main()






