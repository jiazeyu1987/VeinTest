import qt
import slicer.util as util


class ClickableLineEdit(qt.QLineEdit):
    clicked = qt.Signal()

    def __init__(self, name, value, parent=None):
        super().__init__(parent)
        self.setText(value)
        self.previous_value = value
        self.name = name
        util.global_data_map[self.name] = int(value)

    def mousePressEvent(self, event):
        if event.button() == qt.Qt.LeftButton:
            self.clicked.emit()

    def focusOutEvent(self, event):
        min_value, max_value = self.validator().bottom, self.validator().top
        value = float(self.text)
        try:
            if value < min_value or value > max_value:
                raise ValueError("Value out of range")
        except ValueError:
            qt.QMessageBox.warning(self, "输入错误", f"输入值必须小于等于{max_value}。")
            self.setText(self.previous_value)
        util.global_data_map[self.name] = value
        util.getModuleWidget("JUltrasoundGenerator").on_set_power_treat()
        self.setReadOnly(True)
        self.setStyleSheet("")


class ClickableLabel(qt.QWidget):
    def __init__(self, es_name, name, value, unit, min_value, max_value, parent=None):
        super().__init__(parent)
        self.label = qt.QLabel(name)
        self.lineEdit = ClickableLineEdit(es_name, value)
        self.unitLabel = qt.QLabel(unit)

        self.lineEdit.setFixedWidth(100)
        self.unitLabel.setFixedWidth(50)

        self.lineEdit.setValidator(qt.QDoubleValidator(min_value, max_value, 2, self.lineEdit))

        layout = qt.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.unitLabel)
        self.setLayout(layout)

        self.setAutoFillBackground(True)

        self.lineEdit.setReadOnly(True)
        self.lineEdit.clicked.connect(self.on_lineEdit_clicked)

    def on_lineEdit_clicked(self):
        self.lineEdit.previous_value = self.lineEdit.text
        self.setEditable(True)

    def setEditable(self, editable):
        self.lineEdit.setReadOnly(not editable)
        if editable:
            self.lineEdit.setFocus()
            self.lineEdit.setStyleSheet("background-color: black; color: white;")
            self.lineEdit.selectAll()
        else:
            self.lineEdit.setStyleSheet("")
