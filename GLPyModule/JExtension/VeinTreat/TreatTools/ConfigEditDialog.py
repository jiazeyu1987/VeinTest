import qt


class ConfigEditDialog(qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(qt.Qt.FramelessWindowHint)
        self.init_ui()

    def init_ui(self):
        self.textEdit = qt.QTextEdit(self)

        self.okButton = qt.QPushButton('确定', self)
        self.cancelButton = qt.QPushButton('取消', self)
        self.okButton.clicked.connect(lambda: self.accept())
        self.cancelButton.clicked.connect(lambda: self.reject())

        buttonLayout = qt.QHBoxLayout()
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)

        layout = qt.QVBoxLayout()
        layout.addWidget(self.textEdit)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

    def get_text(self):
        return self.textEdit.toPlainText()
