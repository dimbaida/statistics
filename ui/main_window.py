# Form implementation generated from reading ui file 'ui/main.ui'
#
# Created by: PyQt6 UI code generator 6.3.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(240, 220)
        MainWindow.setMinimumSize(QtCore.QSize(240, 220))
        MainWindow.setDocumentMode(False)
        MainWindow.setDockNestingEnabled(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.table = QtWidgets.QTableWidget(self.centralwidget)
        self.table.setGeometry(QtCore.QRect(20, 120, 191, 83))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setKerning(True)
        self.table.setFont(font)
        self.table.setShowGrid(True)
        self.table.setGridStyle(QtCore.Qt.PenStyle.SolidLine)
        self.table.setObjectName("table")
        self.table.setColumnCount(3)
        self.table.setRowCount(3)
        item = QtWidgets.QTableWidgetItem()
        self.table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(2, item)
        self.table.horizontalHeader().setVisible(True)
        self.table.horizontalHeader().setCascadingSectionResizes(True)
        self.table.horizontalHeader().setDefaultSectionSize(50)
        self.table.horizontalHeader().setHighlightSections(True)
        self.table.horizontalHeader().setMinimumSectionSize(20)
        self.table.horizontalHeader().setSortIndicatorShown(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setCascadingSectionResizes(False)
        self.table.verticalHeader().setDefaultSectionSize(20)
        self.table.verticalHeader().setHighlightSections(True)
        self.table.verticalHeader().setMinimumSectionSize(20)
        self.table.verticalHeader().setSortIndicatorShown(False)
        self.table.verticalHeader().setStretchLastSection(True)
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 11, 195, 101))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.rows_label = QtWidgets.QLabel(self.layoutWidget)
        self.rows_label.setObjectName("rows_label")
        self.gridLayout.addWidget(self.rows_label, 0, 0, 1, 1)
        self.rows = QtWidgets.QSpinBox(self.layoutWidget)
        self.rows.setMinimum(1)
        self.rows.setProperty("value", 3)
        self.rows.setObjectName("rows")
        self.gridLayout.addWidget(self.rows, 0, 1, 1, 1)
        self.cols_label = QtWidgets.QLabel(self.layoutWidget)
        self.cols_label.setObjectName("cols_label")
        self.gridLayout.addWidget(self.cols_label, 1, 0, 1, 1)
        self.cols = QtWidgets.QSpinBox(self.layoutWidget)
        self.cols.setMinimum(1)
        self.cols.setProperty("value", 3)
        self.cols.setObjectName("cols")
        self.gridLayout.addWidget(self.cols, 1, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 2, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.table.setSortingEnabled(False)
        item = self.table.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "вар 1"))
        item = self.table.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "вар 2"))
        item = self.table.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "вар 3"))
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "повт 1"))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "повт 2"))
        item = self.table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "повт 3"))
        self.rows_label.setText(_translate("MainWindow", "Кількість варіантів"))
        self.cols_label.setText(_translate("MainWindow", "Кількість повторень"))
        self.pushButton.setText(_translate("MainWindow", "Розрахувати"))
