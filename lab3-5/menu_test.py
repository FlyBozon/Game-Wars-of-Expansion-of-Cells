from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QMenu, QAction, \
    QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QColor, QPen, QPainter, QLinearGradient
from PyQt5.QtCore import Qt, QRectF, QLineF, QPointF
import sys
import json

GRID_SIZE = 50
BOARD_WIDTH = 10
BOARD_HEIGHT = 8


class MenuWindow(QGraphicsView):
    def __init__(self, game_data):
        super().__init__()
        self.setWindowTitle("Wybierz poziom")
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setFixedSize(400, 400)
        self.game_data = game_data
        self.load_levels_summary()
        self.set_background()

    def set_background(self):
        gradient = QLinearGradient(0, 0, 400, 400)
        gradient.setColorAt(0, QColor("#ff9966"))
        gradient.setColorAt(1, QColor("#ff5e62"))
        self.scene.setBackgroundBrush(QBrush(gradient))

    def load_levels_summary(self):
        summary = self.game_data.get("summary", {}).get("levels", {})
        num_levels = len(summary)
        cols = 3  # Number of columns in the menu
        spacing = 100

        for i, (level_name, level_data) in enumerate(summary.items()):
            row = i // cols
            col = i % cols
            x = col * spacing + 50
            y = row * spacing + 50

            level_box = LevelItem(x, y, level_name, level_data.get("stars", 0), self)
            self.scene.addItem(level_box)

    # def start_level(self, level_name):
    #     print(f"Starting level: {level_name}")
    #     level_data = self.game_data.get("levels", {}).get(level_name, {})
    #     if not level_data:
    #         print(f"Error: No data found for level '{level_name}'")
    #         return
    #
    #     # Print level information
    #     print("Level Information:")
    #     print(json.dumps(level_data, indent=4))
    #
    #     self.scene.clear()
    #     game_scene = Level(level_data)  # Load the level with data
    #     self.setScene(game_scene)

    def start_level(self, level_name):
        print(f"Starting level: {level_name}")
        self.scene.clear()
        game_scene = GameScene()
        self.setScene(game_scene)

    def parse_specific_level(self, level_name):
        self.game_data.get("levels", {}).get()
        enemy = {}
        user = {}


        pass


class LevelItem(QGraphicsRectItem):
    def __init__(self, x, y, level_name, stars, menu):
        super().__init__(x, y, 80, 80)
        self.setBrush(QBrush(QColor("lightgray")))
        self.setPen(QPen(Qt.black))
        self.level_name = level_name
        self.menu = menu
        self.default_x = x
        self.default_y = y

        self.text = QGraphicsTextItem(level_name, self)
        self.text.setDefaultTextColor(Qt.black)
        self.text.setPos(x + 20, y + 20)

        for s in range(stars):
            star = QGraphicsTextItem("★", self)
            star.setDefaultTextColor(Qt.yellow)
            star.setPos(x + 20 + s * 15, y + 50)

    def mousePressEvent(self, event):
        self.setScale(1.2)
        self.setPos(self.default_x - 5, self.default_y - 5)

    def mouseReleaseEvent(self, event):
        self.menu.start_level(self.level_name)


class GameScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setBackgroundBrush(QBrush(QColor("#87CEEB")))  #light blue background



class Level(QGraphicsScene):
    def __init__(self, level_data):
        super().__init__()
        self.level_data = level_data
        self.setBackgroundBrush(self.create_background())
        self.load_map()

    def create_background(self):
        gradient = QLinearGradient(0, 0, BOARD_WIDTH * GRID_SIZE, BOARD_HEIGHT * GRID_SIZE)
        gradient.setColorAt(0, QColor(128, 0, 128))  # Dark Purple
        gradient.setColorAt(1, QColor(200, 162, 200))  # Light Purple
        return QBrush(gradient)

    def load_map(self):
        for cell in self.level_data.get("map", []):
            x, y = cell["pos"]
            shape = cell["shape"]
            points = cell["points"]
            color = QColor(cell["color"])
            level = cell.get("level", 1)
            self.addItem(GameCell(x, y, shape, points, color, level))


class GameCell(QGraphicsItem):
    def __init__(self, x, y, shape, points, color, level):
        super().__init__()
        self.x, self.y = x, y
        self.shape = shape
        self.points = points
        self.color = color
        self.level = level
        self.size = GRID_SIZE
        self.setPos(x * GRID_SIZE, y * GRID_SIZE)

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black))

        if self.shape == "c":  # Circle
            painter.drawEllipse(self.boundingRect())
        elif self.shape == "t":  # Triangle
            points = [QPointF(self.size / 2, 0), QPointF(0, self.size), QPointF(self.size, self.size)]
            painter.drawPolygon(*points)
        else:  # Default to rectangle
            painter.drawRect(self.boundingRect())

        # Draw points text
        text = QGraphicsTextItem(str(self.points), self)
        text.setDefaultTextColor(Qt.white)
        text.setPos(self.size / 3, self.size / 3)

        # Draw level-based circles
        for i in range(self.level):
            offset = 5 + i * 10
            painter.setBrush(QBrush(QColor("darkblue")))
            painter.drawEllipse(QPointF(self.size - offset, offset), 4, 4)

def load_game_data(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        summary_levels = data.get("summary", {}).get("levels", {})
        actual_levels = data.get("levels", {})
        if len(summary_levels) != len(actual_levels):
            print("Warning: Mismatch in level count. Using actual levels in file.")
            data["summary"]["levels"] = {lvl: {} for lvl in actual_levels}
        return data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        raise ValueError("Invalid game data file format")


def load_map(game_data, level_name):
    """Retrieves a specific map and its description from the loaded game data."""
    if "levels" not in game_data or level_name not in game_data["levels"]:
        raise ValueError(f"Level '{level_name}' not found in game data")
    return game_data["levels"][level_name]


def map_decoder(game_map, map_description, width, height):
    units = []
    grid_width = width // len(game_map[0])
    grid_height = height // len(game_map)
    unit_counters = {key: 0 for key in map_description}  # Track usage of each unit type
    map_counts = {key: sum(row.count(key) for row in game_map) for key in map_description}  # Count occurrences in map
    desc_counts = {key: len(map_description[key]) for key in map_description}  # Count occurrences in description

    # Validate that the map and description match in unit counts
    for key in map_counts:
        if map_counts[key] != desc_counts.get(key, 0):
            raise ValueError(
                f"Mismatch for '{key}': Map has {map_counts[key]}, but description has {desc_counts.get(key, 0)}")

    for y, row in enumerate(game_map):
        for x, cell in enumerate(row):
            if cell in map_description and unit_counters[cell] < len(map_description[cell]):
                unit_info = map_description[cell][unit_counters[cell]]
                unit = {
                    "x": x * grid_width,
                    "y": y * grid_height,
                    "color": unit_info["color"],
                    "points": unit_info["points"],
                    "evolution": unit_info["evolution"],
                    "kind": unit_info["kind"]
                }
                units.append(unit)
                unit_counters[cell] += 1

    return units


if __name__ == "__main__":
    game_data_file = "game_data.json"
    game_data = load_game_data(game_data_file)

    app = QApplication(sys.argv)
    menu = MenuWindow(game_data)
    menu.show()
    sys.exit(app.exec_())
