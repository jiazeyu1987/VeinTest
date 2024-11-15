import qt
import slicer
import slicer.util as util
import os


class HistoryDetailPanel:
    def __init__(self, vein_info, detail_info):
        current_file_path = os.path.abspath(__file__)

        parent_directory = os.path.dirname(os.path.dirname(current_file_path))

        self.uiWidget = slicer.util.loadUI(parent_directory + '/Resources/UI/DetailInfo.ui')
        self.ui = util.childWidgetVariables(self.uiWidget)
        self.vein_info = vein_info
        self.detail_info = detail_info
        self.selected_rect = None
        self.selected_thumbnail = None

        self._init_ui()

    def _init_ui(self):
        self.uiWidget.setWindowTitle('历史详情')
        self.uiWidget.setGeometry(100, 100, 1400, 1100)

        self.scene = qt.QGraphicsScene()
        self.ui.scroll_images.setScene(self.scene)
        self.ui.scroll_images.setHorizontalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOff)
        self.ui.scroll_images.setVerticalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOff)
        self.ui.scroll_images.setDragMode(qt.QGraphicsView.ScrollHandDrag)
        self.ui.label_vein_info.setText(self.vein_info)

        self.ui.thumbnail_scroll_area.setWidgetResizable(True)
        self.ui.thumbnail_scroll_area.setFixedHeight(80)
        self.scroll_layout = qt.QHBoxLayout(self.ui.scroll_images)
        self.thumbnail_layout = qt.QHBoxLayout(self.ui.thumbnail_scroll_area)

        self.ui.label_info.setFrameStyle(qt.QFrame.Panel | qt.QFrame.Sunken)

        self.load_images()

    def load_images(self):
        Pos, Power, Energy, image_list = self.detail_info
        label = "位置: 512" + "\n功率: 1024" + "\n能量: 2048"
        images = image_list.split(";")
        image_items = list()
        x_offset = 0

        for index, image in enumerate(images):  # Add image to scene
            index_label = "序号" + str(index) + "\n" + label
            pixmap = qt.QPixmap(image)
            item = qt.QGraphicsPixmapItem(pixmap)
            item.setPos(x_offset, 0)
            item.setData(0, index_label)
            self.scene.addItem(item)
            image_items.append(item)

            image_names = image.split("/")[-1].split(".")
            text_item = qt.QGraphicsTextItem(image.split("/")[-1].split(".")[0])
            # text_item.setPos(x_offset + pixmap.width() / 2 - text_item.boundingRect().width() / 2,
            #                  pixmap.height() + 5)
            text_item.setFont(qt.QFont("Arial", 20, qt.QFont.Bold))
            # text_item.setDefaultTextColor(qt.Qt.black)
            rect_item = qt.QGraphicsRectItem(text_item.boundingRect())
            rect_item.setBrush(qt.QBrush(qt.QColor(173, 216, 230)))
            rect_item.setPen(qt.QPen(qt.Qt.NoPen))
            rect_item.setPos(text_item.pos)

            text_item.setParentItem(rect_item)
            rect_item.setPos(x_offset + pixmap.width() / 2 - text_item.boundingRect().width() / 2,
                             pixmap.height() + 5)
            item.setData(1, text_item)
            if len(image_names) == 3:
                self.highlight_item(item, True)
            self.scene.addItem(rect_item)

            x_offset += pixmap.width()

            thumbnail_label = ClickableLabel(item, index_label, self)
            thumbnail_pixmap = pixmap.scaled(200, 200, qt.Qt.KeepAspectRatio)
            thumbnail_label.setPixmap(thumbnail_pixmap)
            self.thumbnail_layout.addWidget(thumbnail_label)

        # Set the scene size
        if image_items:
            self.scene.setSceneRect(0, 0, x_offset,
                                    image_items[0].pixmap().height() + 50)  # Adjust scene size to include text

    def center_on_item(self, item):
        self.ui.scroll_images.centerOn(item)

    def display_image_info(self, image_info):
        self.ui.label_info.setText(image_info)

    def highlight_item(self, item, flag=False):
        if self.selected_rect and not flag:
            self.scene.removeItem(self.selected_rect)

        rect = item.boundingRect()
        text_item = item.data(1)
        text_rect = text_item.boundingRect()

        combined_rect = rect.united(qt.QRectF(
            rect.x(), rect.y(),
            rect.width(), rect.height() + text_rect.height() + 5
        ))
        if flag:
            blue_rect = self.scene.addRect(combined_rect, qt.QPen(qt.Qt.blue, 3))
            blue_rect.setPos(item.pos())
            return
        self.selected_rect = self.scene.addRect(combined_rect, qt.QPen(qt.Qt.yellow, 3))
        self.selected_rect.setPos(item.pos())

    def highlight_thumbnail(self, thumbnail):
        if self.selected_thumbnail:
            self.selected_thumbnail.setStyleSheet("")
        thumbnail.setStyleSheet("border: 2px solid yellow;")
        self.selected_thumbnail = thumbnail

    def show(self):
        self.uiWidget.show()

    def hide(self):
        self.uiWidget.hide()


class ClickableLabel(qt.QLabel):
    def __init__(self, item, info, parent):
        super().__init__(parent)
        self.item = item
        self.info = info
        self.parent_window = parent
        self.setFixedWidth(200)  # 设置固定宽度

    def mousePressEvent(self, event):
        self.parent_window.center_on_item(self.item)
        self.parent_window.display_image_info(self.info)
        self.parent_window.highlight_item(self.item)
        self.parent_window.highlight_thumbnail(self)
