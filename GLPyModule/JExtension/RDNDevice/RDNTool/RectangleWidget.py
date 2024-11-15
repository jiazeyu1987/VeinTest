import slicer
import vtk


class RectangleWidget:
    def __init__(self):
        self.red_widget = slicer.app.layoutManager().sliceWidget('Red')
        self.slice_view = self.red_widget.sliceView()
        self.slice_logic = self.red_widget.sliceLogic()
        self.interactor = self.slice_view.interactorStyle().GetInteractor()

        self.renderer = self.slice_view.renderWindow().GetRenderers().GetFirstRenderer()
        self.rect = [50, 50, 200, 150]
        self.corner_size = 10
        self.dragging = False
        self.resizing = False
        self.corner_dragging = None
        self.drawing = False

        self.rect_actor = self.create_actor(0, 1, 0, 2)
        self.corner_actors = [self.create_actor(1, 0, 0) for _ in range(4)]

        self.left_button_press_observer = None
        self.mouse_move_observer = None
        self.left_button_release_observer = None

        self.add_event_listeners()

    def create_actor(self, r, g, b, line_width=None):
        actor = vtk.vtkActor2D()
        actor.GetProperty().SetColor(r, g, b)
        if line_width:
            actor.GetProperty().SetLineWidth(line_width)
        return actor

    def create_rectangle(self):
        self.update_rectangle()
        self.renderer.AddActor2D(self.rect_actor)
        for actor in self.corner_actors:
            self.renderer.AddActor2D(actor)
        self.slice_view.scheduleRender()

    def update_rectangle(self):
        points, lines = self.create_rectangle_points()
        poly_data = self.create_poly_data(points, lines)

        mapper = vtk.vtkPolyDataMapper2D()
        mapper.SetInputData(poly_data)

        self.rect_actor.SetMapper(mapper)
        self.update_corners()
        self.get_rectangle_position()
        self.slice_view.scheduleRender()

    def create_rectangle_points(self):
        points = vtk.vtkPoints()
        points.InsertNextPoint(self.rect[0], self.rect[1], 0)
        points.InsertNextPoint(self.rect[0] + self.rect[2], self.rect[1], 0)
        points.InsertNextPoint(self.rect[0] + self.rect[2], self.rect[1] + self.rect[3], 0)
        points.InsertNextPoint(self.rect[0], self.rect[1] + self.rect[3], 0)

        lines = vtk.vtkCellArray()
        lines.InsertNextCell(5)
        lines.InsertCellPoint(0)
        lines.InsertCellPoint(1)
        lines.InsertCellPoint(2)
        lines.InsertCellPoint(3)
        lines.InsertCellPoint(0)
        return points, lines

    def create_poly_data(self, points, lines):
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetLines(lines)
        return poly_data

    def update_corners(self):
        for i, corner in enumerate(self.get_corners()):
            circle_source = self.create_circle_source(corner)
            glyph_mapper = vtk.vtkPolyDataMapper2D()
            glyph_mapper.SetInputConnection(circle_source.GetOutputPort())
            self.corner_actors[i].SetMapper(glyph_mapper)

    def create_circle_source(self, corner):
        circle_source = vtk.vtkRegularPolygonSource()
        circle_source.SetNumberOfSides(20)  # Higher number of sides for smoother circle
        circle_source.SetRadius(self.corner_size / 2.0)
        circle_source.SetCenter(corner[0], corner[1], 0)
        circle_source.Update()
        return circle_source

    def add_event_listeners(self):
        self.left_button_press_observer = self.interactor.AddObserver("LeftButtonPressEvent", self.on_mouse_press)
        self.mouse_move_observer = self.interactor.AddObserver("MouseMoveEvent", self.on_mouse_move)
        self.left_button_release_observer = self.interactor.AddObserver("LeftButtonReleaseEvent", self.on_mouse_release)

    def remove_event_listeners(self):
        if self.left_button_press_observer is not None:
            self.interactor.RemoveObserver(self.left_button_press_observer)
            self.left_button_press_observer = None
        if self.mouse_move_observer is not None:
            self.interactor.RemoveObserver(self.mouse_move_observer)
            self.mouse_move_observer = None
        if self.left_button_release_observer is not None:
            self.interactor.RemoveObserver(self.left_button_release_observer)
            self.left_button_release_observer = None

    def on_mouse_press(self, caller, event):
        if not self.drawing:
            return
        click_pos = self.interactor.GetEventPosition()
        if self.check_corner_resize(click_pos):
            return
        if self.point_in_rect(click_pos, self.rect):
            self.dragging = True
            self.drag_start_position = (click_pos[0] - self.rect[0], click_pos[1] - self.rect[1])

    def check_corner_resize(self, click_pos):
        for i, corner in enumerate(self.get_corners()):
            if self.point_in_circle(click_pos, corner, self.corner_size / 2.0):
                self.resizing = True
                self.corner_dragging = i
                self.drag_start_position = click_pos
                return True
        return False

    def on_mouse_move(self, caller, event):
        if not self.drawing:
            return
        move_pos = self.interactor.GetEventPosition()
        if self.dragging:
            self.update_rectangle_position(move_pos)
        elif self.resizing and self.corner_dragging is not None:
            self.resize_rectangle(move_pos)

    def update_rectangle_position(self, move_pos):
        self.rect[0] = move_pos[0] - self.drag_start_position[0]
        self.rect[1] = move_pos[1] - self.drag_start_position[1]
        self.update_rectangle()

    def on_mouse_release(self, caller, event):
        if not self.drawing:
            return
        self.dragging = False
        self.resizing = False
        self.corner_dragging = None

    def get_corners(self):
        return [
            [self.rect[0], self.rect[1]],  # 左上角
            [self.rect[0] + self.rect[2], self.rect[1]],  # 右上角
            [self.rect[0], self.rect[1] + self.rect[3]],  # 左下角
            [self.rect[0] + self.rect[2], self.rect[1] + self.rect[3]],  # 右下角
        ]

    def point_in_rect(self, point, rect):
        return rect[0] <= point[0] <= rect[0] + rect[2] and rect[1] <= point[1] <= rect[1] + rect[3]

    def point_in_circle(self, point, center, radius):
        return (point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2 <= radius ** 2

    def resize_rectangle(self, pos):
        if self.corner_dragging == 0:
            new_width = self.rect[2] - (pos[0] - self.rect[0])
            new_height = self.rect[3] - (pos[1] - self.rect[1])
            if new_width > 0 and new_height > 0:
                self.rect[2] = new_width
                self.rect[3] = new_height
                self.rect[0] = pos[0]
                self.rect[1] = pos[1]
        elif self.corner_dragging == 1:
            new_width = pos[0] - self.rect[0]
            new_height = self.rect[3] - (pos[1] - self.rect[1])
            if new_width > 0 and new_height > 0:
                self.rect[2] = new_width
                self.rect[3] = new_height
                self.rect[1] = pos[1]
        elif self.corner_dragging == 2:
            new_width = self.rect[2] - (pos[0] - self.rect[0])
            new_height = pos[1] - self.rect[1]
            if new_width > 0 and new_height > 0:
                self.rect[2] = new_width
                self.rect[0] = pos[0]
                self.rect[3] = new_height
        elif self.corner_dragging == 3:
            new_width = pos[0] - self.rect[0]
            new_height = pos[1] - self.rect[1]
            if new_width > 0 and new_height > 0:
                self.rect[2] = new_width
                self.rect[3] = new_height
        self.update_rectangle()

    def get_rectangle_position(self):
        # 获取矩形左下角坐标和长宽
        left_bottom_corner = [self.rect[0], self.rect[1]]
        width = self.rect[2]
        height = self.rect[3]

        # 获取 SliceNode 的矩阵转换
        slice_node = self.slice_logic.GetSliceNode()
        xy_to_ras_matrix = slice_node.GetXYToRAS()

        # 将左下角坐标转换到 RAS 坐标系
        ras_point = [0.0, 0.0, 0.0, 1.0]
        xy_point = [left_bottom_corner[0], left_bottom_corner[1], 0.0, 1.0]
        xy_to_ras_matrix.MultiplyPoint(xy_point, ras_point)
        # print(f"point is ---- {ras_point, width, height}")

        # 输出 RAS 坐标和长宽
        return {
            "RAS Coordinates": (ras_point[0], ras_point[1], ras_point[2]),
            "Width": width,
            "Height": height
        }

    def set_rectangle_position(self, ras_x, ras_y, width, height):
        ras_point = [ras_x, ras_y, 0.0, 1.0]

        slice_node = self.slice_logic.GetSliceNode()
        xy_to_ras_matrix = slice_node.GetXYToRAS()

        # 获取逆矩阵
        ras_to_xy_matrix = vtk.vtkMatrix4x4()
        vtk.vtkMatrix4x4.Invert(xy_to_ras_matrix, ras_to_xy_matrix)

        xy_point = [0.0, 0.0, 0.0, 1.0]
        ras_to_xy_matrix.MultiplyPoint(ras_point, xy_point)
        # print(f"Converted XY coordinates: {xy_point[:2]}")  # 调试信息

        self.rect[0] = xy_point[0]
        self.rect[1] = xy_point[1]
        self.rect[2] = width
        self.rect[3] = height

        self.update_rectangle()

    def start_drawing(self):
        self.drawing = True
        self.rect = [50, 50, 200, 150]
        self.create_rectangle()  # Draw the rectangle when starting drawing

    def clear_rectangle(self):
        self.remove_event_listeners()
        if self.rect_actor and self.renderer.HasViewProp(self.rect_actor):
            self.renderer.RemoveActor2D(self.rect_actor)

        for actor in self.corner_actors:
            if actor and self.renderer.HasViewProp(actor):
                self.renderer.RemoveActor2D(actor)

        self.slice_view.scheduleRender()
        self.drawing = False

        self.add_event_listeners()
