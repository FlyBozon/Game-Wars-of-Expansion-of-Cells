from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QMenu, QAction
from PyQt5.QtGui import QBrush, QColor, QPen, QPainter
from PyQt5.QtCore import Qt, QRectF, QLineF
import sys

# Stałe dla planszy
GRID_SIZE = 50  # Rozmiar siatki
BOARD_WIDTH = 10
BOARD_HEIGHT = 8

class Unit(QGraphicsItem):
    def __init__(self, x, y, color, game_scene):
        super().__init__()
        self.setPos(x * GRID_SIZE, y * GRID_SIZE)
        self.color = color
        self.original_size = GRID_SIZE
        self.is_selected = False
        self.game_scene = game_scene
        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable)

    def boundingRect(self):
        size = self.original_size * (1.2 if self.is_selected else 1.0)
        return QRectF(0, 0, size, size)

    def paint(self, painter, option, widget):
        size = self.original_size * (1.2 if self.is_selected else 1.0)
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(0, 0, size, size)

    def mousePressEvent(self, event):
        if self.color == QColor("blue"):
            self.is_selected = True
            self.update()
            self.game_scene.selected_unit = self
        elif self.color == QColor("red") and self.game_scene.selected_unit:
            self.game_scene.draw_connection(self.game_scene.selected_unit, self)
            self.game_scene.selected_unit.is_selected = False
            self.game_scene.selected_unit.update()
            self.game_scene.selected_unit = None
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu()
        move_action = QAction("Przesuń", None)
        move_action.triggered.connect(lambda: print("Przesuwanie jednostki"))
        menu.addAction(move_action)
        menu.exec_(event.screenPos())

class GameScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, BOARD_WIDTH * GRID_SIZE, BOARD_HEIGHT * GRID_SIZE)
        self.draw_grid()
        self.units = []
        self.selected_unit = None
        self.add_units()
        self.lines = []

    def draw_grid(self):
        for x in range(0, BOARD_WIDTH * GRID_SIZE, GRID_SIZE):
            for y in range(0, BOARD_HEIGHT * GRID_SIZE, GRID_SIZE):
                self.addRect(x, y, GRID_SIZE, GRID_SIZE, QPen(Qt.black))

    def add_units(self):
        unit1 = Unit(2, 3, QColor("blue"), self)
        unit2 = Unit(5, 5, QColor("red"), self)
        self.addItem(unit1)
        self.addItem(unit2)
        self.units.append(unit1)
        self.units.append(unit2)

    def draw_connection(self, unit1, unit2):
        line = self.addLine(QLineF(unit1.pos() + QPointF(GRID_SIZE / 2, GRID_SIZE / 2),
                                   unit2.pos() + QPointF(GRID_SIZE / 2, GRID_SIZE / 2)),
                            QPen(Qt.black, 2))
        self.lines.append(line)

class GameView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(GameScene())
        self.setRenderHint(QPainter.Antialiasing)
        self.setFixedSize(BOARD_WIDTH * GRID_SIZE + 10, BOARD_HEIGHT * GRID_SIZE + 10)
        self.setWindowTitle("Wojna Ekspansji")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = GameView()
    view.show()
    sys.exit(app.exec_())
