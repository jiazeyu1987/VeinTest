import qt


class LineWidget(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.current_step = 0
        self.total_steps = 3
        self.blink = False

        self.timer = qt.QTimer(self)
        self.timer.timeout.connect(self.toggle_blink)
        self.timer.start(500)

    def toggle_blink(self):
        self.blink = not self.blink
        self.update()

    def move_next(self):
        if self.current_step >= self.total_steps - 1:
            self.total_steps += 1
        self.current_step += 1
        self.update()

    def move_pre(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update()

    def paintEvent(self, event):
        painter = qt.QPainter(self)
        painter.setRenderHint(qt.QPainter.Antialiasing)

        # Draw the red line
        painter.setPen(qt.QPen(qt.QColor('red'), 2))
        painter.drawLine(50, 10, 50, self.height - 10)

        step_height = (self.height - 20) / (self.total_steps - 1)
        for i in range(self.total_steps):
            y = 10 + i * step_height
            if i == self.current_step and self.blink:
                painter.setBrush(qt.QColor('blue'))
            else:
                painter.setBrush(qt.QColor('white'))
            painter.drawEllipse(45, int(y - 5), 10, 10)

        # Draw start label
        painter.setPen(qt.QPen(qt.QColor('white'), 2))
        painter.drawText(60, 20, "Start")

    def set_step(self, step):
        self.total_steps = step
        self.current_step = 0
        self.update()

    def get_step(self):
        return self.current_step
