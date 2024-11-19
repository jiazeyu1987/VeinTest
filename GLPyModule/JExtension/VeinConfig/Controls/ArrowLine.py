from qt import QWidget, QApplication, QGraphicsItem, QGraphicsScene, QGraphicsView
from qt import QPainter, QPen, QBrush, QColor, QPainterPath
from qt import Qt, QPointF, QRectF
import sys
import math

class ArrowLine(QGraphicsItem):
    def __init__(self, startpos, endpos, controlpos, color=QColor("#F1675E")):
        super().__init__()

        self.start_point = startpos
        self.control_point = controlpos
        self.end_point = endpos
        self.color = color

        self.width = 300
        self.height = 300
    def boundingRect(self):


        # 返回按钮的边界矩形
        return QRectF(0, 0, self.width, self.height)
    def paint(self, painter, option, widget=None):

        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.color, 2)
        painter.setPen(pen)

        # 绘制二次贝塞尔曲线
        path = self.quadratic_bezier_path(self.start_point, self.control_point, self.end_point)
        painter.drawPath(path)

        # 绘制起点和终点的箭头
        self.draw_arrow(painter, self.start_point, self.control_point, reverse=False)
        self.draw_arrow(painter, self.end_point, self.control_point)

    def quadratic_bezier_path(self, start, control, end):
        """生成二次贝塞尔曲线的路径"""
        path = QPainterPath()
        path.moveTo(start)
        path.quadTo(control, end)
        return path

    def draw_arrow(self, painter, point, control, arrow_size=10, reverse=False):
        """绘制箭头"""
        # 计算箭头方向向量
        if reverse:
            direction = point - control
        else:
            direction = control - point
        angle = math.atan2(direction.y(), direction.x())

        # 计算箭头的两个边点
        arrow_p1 = QPointF(
            point.x() + arrow_size * math.cos(angle + math.pi / 9),
            point.y() + arrow_size * math.sin(angle + math.pi / 9)
        )
        arrow_p2 = QPointF(
            point.x() + arrow_size * math.cos(angle - math.pi / 9),
            point.y() + arrow_size * math.sin(angle - math.pi / 9)
        )

        # 绘制箭头
        arrow_head = QPainterPath()
        arrow_head.moveTo(point)
        arrow_head.lineTo(arrow_p1)
        arrow_head.lineTo(arrow_p2)
        arrow_head.closeSubpath()

        painter.setBrush(QBrush(self.color))
        painter.drawPath(arrow_head)

def main():
    app = QApplication(sys.argv)
    scene = QGraphicsScene()
    view = QGraphicsView()

    view.setScene(scene)

    arrow = ArrowLine(startpos=QPointF(50, 50), endpos=QPointF(150,100), controlpos=QPointF(70, 80))
    scene.addItem(arrow)

    view.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
