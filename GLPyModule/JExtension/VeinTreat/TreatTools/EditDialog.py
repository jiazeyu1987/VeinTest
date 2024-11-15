import qt


class EditDialog(qt.QDialog):
    def __init__(self, parameters, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Parameters")
        self.parameters = parameters

        self.mainLayout = qt.QVBoxLayout()

        self.tableWidget = qt.QTableWidget(len(parameters), 2)
        self.tableWidget.setHorizontalHeaderLabels(["参数", "值"])
        for i, (param, value) in enumerate(parameters.items()):
            param_item = qt.QTableWidgetItem(param)
            param_item.setFlags(param_item.flags() & ~qt.Qt.ItemIsEditable)  # 设置参数名不可编辑
            self.tableWidget.setItem(i, 0, param_item)
            self.tableWidget.setItem(i, 1, qt.QTableWidgetItem(value))

        self.mainLayout.addWidget(self.tableWidget)

        self.buttonLayout = qt.QHBoxLayout()
        self.confirmButton = qt.QPushButton("确认")
        self.cancelButton = qt.QPushButton("取消")
        self.buttonLayout.addWidget(self.confirmButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.mainLayout.addLayout(self.buttonLayout)

        self.setLayout(self.mainLayout)

        self.confirmButton.connect("clicked()", self.accept)
        self.cancelButton.connect("clicked()", self.reject)

    def getParameters(self):
        updated_parameters = {}
        for i in range(self.tableWidget.rowCount):
            param = self.tableWidget.item(i, 0).text()
            value = self.tableWidget.item(i, 1).text()
            updated_parameters[param] = value
        return updated_parameters
