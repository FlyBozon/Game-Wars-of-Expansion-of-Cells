"""
added:
- map loading and decoding
- choosing level from menu
- level loading
- opportunity to choose cell and attack
- connections between cells and balls that fly between cells

current TODO:
1. add stoppers to balls number
2. winning strategy
3. update game logic, add more enemies
4. add empty cells (cells in json already excists, but add some logic to them)
5. add enemy pseudo AI


zalozenia projektowe:
    QGraphicsScene – implementacja sceny gry (1 pkt)
    Dziedziczenie po QGraphicsItem – jednostki jako osobne obiekty (1 pkt)
    Interaktywność jednostek – klikalność, przeciąganie, menu kontekstowe (3 pkt)
    Sterowanie jednostkami – wybór z menu i ruch na siatce planszy (2 pkt)
    Zaciąganie grafik jednostek z pliku .rc (1 pkt)
    Podświetlanie możliwych ruchów i ataków w zależności od mnożnika (2 pkt)
    System walki uwzględniający poziomy, mnożenie jednostek i specjalne efekty bitewne (3 pkt)
    Mechanizm tur i licznik czasu na wykonanie ruchu (zegar rundowy) (2 pkt)
    System podpowiedzi strategicznych oparty na AI (np. najlepszy ruch w turze) (1 pkt)
    Sterowanie jednostkami za pomocą gestów z kamery (kliknięcie ruchem dłoni) (1 pkt)
    Logger wyświetlający komunikaty na konsoli i w interfejsie QTextEdit z rotującym logowaniem (1 pkt)
    Przełączanie widoku między 2D i 3D (w tym renderowanie jednostek w 3D) (2 pkt)
"""
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QMenu, QAction, \
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem
from PyQt5.QtGui import QBrush, QColor, QPen, QPainter, QLinearGradient
from PyQt5.QtCore import Qt, QRectF, QLineF, QPointF, QTimer
import sys
import json

GRID_SIZE = 50
BOARD_WIDTH = 10
BOARD_HEIGHT = 30

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
        cols = 3  # number of columns in the menu
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
        level_data = self.game_data.get("levels", {}).get(level_name, {})
        if not level_data:
            print(f"Error: No data found for level '{level_name}'")
            return

        self.scene.clear()
        game_scene = GameScene(level_data)
        self.setScene(game_scene)

#level parser
def extract_game_objects(level_data):
    game_objects = []
    game_map = level_data["map"]
    description = level_data.get("description", {})

    object_counters = {key: 0 for key in description}

    for y, row in enumerate(game_map):
        for x, cell in enumerate(row):
            if cell in description and object_counters[cell] < len(description[cell]):
                obj_info = description[cell][object_counters[cell]]
                game_objects.append({
                    "x": x,
                    "y": y,
                    "type": cell,
                    "points": obj_info["points"],
                    "evolution": obj_info["evolution"],
                    "kind": obj_info["kind"],
                    "color": obj_info["color"]
                })
                object_counters[cell] += 1

    return game_objects

class GameScene(QGraphicsScene):
    def __init__(self, level_data):
        super().__init__()
        self.setBackgroundBrush(QBrush(QColor("#87CEEB")))
        self.level_data = level_data
        self.load_level()
        self.connections = []
        self.selected_cell = None

        upd_time=3000
        self.timer=QTimer()
        self.timer.timeout.connect(self.update_cells)
        self.timer.start(upd_time)

    def load_level(self):
        objects = extract_game_objects(self.level_data)
        for obj in objects:
            item = GameCell(obj["x"], obj["y"], obj["kind"], obj["points"], QColor(obj["color"]), obj["evolution"])
            self.addItem(item)

    def select_cell(self, cell):
        if self.selected_cell is None:
            self.selected_cell = cell
            cell.enlarge()
        else:
            if self.selected_cell != cell:
                connection = ConnectionLine(self.selected_cell, cell, self)
                self.addItem(connection)
                self.connections.append(connection)
            self.selected_cell.shrink()
            self.selected_cell = None

    def remove_connections(self, cell):
        to_remove = []
        for connection in self.connections:
            if connection.start_cell == cell or connection.end_cell == cell:
                to_remove.append(connection)

        for connection in to_remove:
            connection.remove_connection()
            self.connections.remove(connection)

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if isinstance(item, ConnectionLine):
            item.remove_connection()
            self.connections.remove(item)
        else:
            super().mousePressEvent(event)

    def update_cells(self):
        for item in self.items():
            if isinstance(item, GameCell):
                item.points += 1
                item.update()


class TransferBall(QGraphicsEllipseItem):
    def __init__(self, start_cell, end_cell, scene, connection):
        super().__init__(-5, -5, 10, 10)
        self.start_cell = start_cell
        self.end_cell = end_cell
        self.scene = scene
        self.connection = connection
        self.setBrush(QColor(start_cell.color))

        cell_speed = 300
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_ball)
        self.timer.start(cell_speed)

    def move_ball(self):
        self.progress += 0.1
        if self.progress >= 1.0:
            self.hit_target()
            return

        start_pos = self.start_cell.pos()
        end_pos = self.end_cell.pos()
        new_x = start_pos.x() + self.progress * (end_pos.x() - start_pos.x())
        new_y = start_pos.y() + self.progress * (end_pos.y() - start_pos.y())
        self.setPos(new_x, new_y)

    def hit_target(self):
        if self.start_cell.color == self.end_cell.color:
            self.end_cell.points += 1
        else:
            self.end_cell.points = max(0, self.end_cell.points - 1)
            if self.end_cell.points == 0:
                self.end_cell.color = self.start_cell.color #change cell color to enemy's one
                self.scene.remove_connections(self.end_cell)

        self.end_cell.update()
        self.scene.removeItem(self)


class ConnectionLine(QGraphicsLineItem):
    def __init__(self, start_cell, end_cell, scene):
        super().__init__()
        self.start_cell = start_cell
        self.end_cell = end_cell
        self.scene = scene
        self.setPen(QPen(Qt.black, 2))
        self.update_line()

        self.balls = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.spawn_ball)
        self.timer.start(500)

    def update_line(self):
        self.setLine(QLineF(self.start_cell.pos(), self.end_cell.pos()))

    def spawn_ball(self):
        ball = TransferBall(self.start_cell, self.end_cell, self.scene, self)
        self.scene.addItem(ball)
        self.balls.append(ball)

    def remove_connection(self):
        self.timer.stop()
        for ball in self.balls:
            self.scene.removeItem(ball)
        self.scene.removeItem(self)

class GameCell(QGraphicsItem):
    def __init__(self, x, y, shape, points, color, level):
        super().__init__()
        self.x, self.y = x, y
        self.shape = shape
        self.points = points
        self.color = color
        self.level = level
        self.default_size = GRID_SIZE
        self.size = self.default_size
        self.setPos(x * GRID_SIZE, y * GRID_SIZE)

        self.points_text = QGraphicsTextItem(str(self.points), self)
        self.points_text.setDefaultTextColor(Qt.white)
        self.points_text.setPos(self.size / 3, self.size / 3)

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black))

        if self.shape == "c":  # circle
            painter.drawEllipse(self.boundingRect())
        elif self.shape == "t":  #triangle
            points = [QPointF(self.size / 2, 0), QPointF(0, self.size), QPointF(self.size, self.size)]
            painter.drawPolygon(*points)
        else:  #default - rectangle
            painter.drawRect(self.boundingRect())

#show cell level (1,2 or 3)
        for i in range(self.level):
            offset = 5 + i * 10
            painter.setBrush(QBrush(QColor("darkblue")))
            painter.drawEllipse(QPointF(self.size - offset, offset), 4, 4)

#update cell data
    def update(self):
        self.points_text.setPlainText(str(self.points))
        self.points_text.setPos(self.size / 3, self.size / 3)
        super().update()

    def enlarge(self):
        self.setScale(1.2)
        self.update()

    def shrink(self):
        self.setScale(1.0)
        self.update()

    def mousePressEvent(self, event):
        self.scene().select_cell(self)

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
    unit_counters = {key: 0 for key in map_description}
    map_counts = {key: sum(row.count(key) for row in game_map) for key in map_description}
    desc_counts = {key: len(map_description[key]) for key in map_description}

#check if map is correct
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
