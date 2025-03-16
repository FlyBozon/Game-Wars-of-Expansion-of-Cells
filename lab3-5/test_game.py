from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsTextItem, QGraphicsRectItem
from PyQt5.QtGui import QBrush, QColor, QPen, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF
import sys
import json

GRID_SIZE = 50
BOARD_WIDTH = 10
BOARD_HEIGHT = 10

class MenuWindow(QGraphicsView):
    def __init__(self, game_data):
        super().__init__()
        self.setWindowTitle("Wybierz poziom")
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setFixedSize(400, 400)
        self.game_data = game_data
        self.load_levels()

    def load_levels(self):
        summary = self.game_data.get("summary", {}).get("levels", {})
        cols = 3
        spacing = 100

        for i, (level_name, level_data) in enumerate(summary.items()):
            row = i // cols
            col = i % cols
            x = col * spacing + 50
            y = row * spacing + 50

            level_box = LevelItem(x, y, level_name, level_data.get("stars", 0), self)
            self.scene.addItem(level_box)

    def start_level(self, level_name):
        print(f"Starting level: {level_name}")
        self.scene.clear()
        level_data = self.game_data.get("levels", {}).get(level_name, {})
        if not level_data:
            print("No data found for this level!")
            return
        game_scene = Level(level_data)
        self.setScene(game_scene)

class LevelItem(QGraphicsRectItem):
    def __init__(self, x, y, level_name, stars, menu):
        super().__init__(x, y, 80, 80)
        self.setBrush(QBrush(QColor("lightgray")))
        self.setPen(QPen(Qt.black))
        self.level_name = level_name
        self.menu = menu
        self.text = QGraphicsTextItem(level_name, self)
        self.text.setDefaultTextColor(Qt.black)
        self.text.setPos(x + 10, y + 10)

    def mouseReleaseEvent(self, event):
        self.menu.start_level(self.level_name)

class Level(QGraphicsScene):
    def __init__(self, level_data):
        super().__init__()
        self.level_data = level_data
        self.setBackgroundBrush(QBrush(QColor(128, 0, 128)))
        self.load_map()

    def load_map(self):
        game_map = self.level_data.get("map", [])
        descriptions = self.level_data.get("description", {})

        for y, row in enumerate(game_map):
            for x, cell in enumerate(row):
                if cell in descriptions:
                    for entity in descriptions[cell]:
                        self.addItem(GameCell(x, y, entity))

class GameCell(QGraphicsItem):
    def __init__(self, x, y, entity):
        super().__init__()
        self.x, self.y = x, y
        self.points = entity["points"]
        self.evolution = entity["evolution"]
        self.shape = entity["kind"]
        self.color = QColor(entity["color"]) if entity["color"] != "no" else QColor(Qt.gray)
        self.size = GRID_SIZE
        self.setPos(x * GRID_SIZE, y * GRID_SIZE)

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black))

        if self.shape == "c":
            painter.drawEllipse(self.boundingRect())
        elif self.shape == "t":
            points = [QPointF(self.size / 2, 0), QPointF(0, self.size), QPointF(self.size, self.size)]
            painter.drawPolygon(*points)
        else:
            painter.drawRect(self.boundingRect())

        text = QGraphicsTextItem(str(self.points), self)
        text.setDefaultTextColor(Qt.white)
        text.setPos(self.size / 3, self.size / 3)

# Load game data

def load_game_data(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error loading game data.")
        return {}

if __name__ == "__main__":
    game_data_file = "game_data.json"
    game_data = load_game_data(game_data_file)
    app = QApplication(sys.argv)
    menu = MenuWindow(game_data)
    menu.show()
    sys.exit(app.exec_())
