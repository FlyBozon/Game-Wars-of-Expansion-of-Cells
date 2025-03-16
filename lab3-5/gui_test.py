from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, \
    QGraphicsTextItem
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QPointF
import sys
from PyQt5.QtGui import QPainter


# Sample input data
nodes = [
    {"id": 1, "value": 33, "x": 200, "y": 50},
    {"id": 2, "value": 32, "x": 400, "y": 150},
    {"id": 3, "value": 35, "x": 300, "y": 350},
    {"id": 4, "value": 13, "x": 200, "y": 450},
    {"id": 5, "value": 19, "x": 400, "y": 300},
    {"id": 6, "value": 17, "x": 100, "y": 300},
    {"id": 7, "value": 17, "x": 500, "y": 300},
    {"id": 8, "value": 15, "x": 600, "y": 150},
]

edges = [
    {"from": 1, "to": 2, "color": "pink"},
    {"from": 2, "to": 5, "color": "green"},
    {"from": 5, "to": 3, "color": "green"},
    {"from": 3, "to": 4, "color": "yellow"},
    {"from": 4, "to": 6, "color": "pink"},
    {"from": 6, "to": 1, "color": "pink"},
    {"from": 2, "to": 7, "color": "yellow"},
    {"from": 7, "to": 3, "color": "yellow"},
    {"from": 2, "to": 8, "color": "yellow"},
]


class GraphView(QGraphicsView):
    def __init__(self, nodes, edges):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.node_map = {}
        self.draw_graph(nodes, edges)
        self.setFixedSize(800, 600)

    def draw_graph(self, nodes, edges):
        # Draw edges first
        for edge in edges:
            node_from = next(n for n in nodes if n["id"] == edge["from"])
            node_to = next(n for n in nodes if n["id"] == edge["to"])

            line = QGraphicsLineItem(node_from["x"], node_from["y"], node_to["x"], node_to["y"])
            color = QColor(edge["color"])
            line.setPen(QPen(color, 4))
            self.scene.addItem(line)

        # Draw nodes
        for node in nodes:
            ellipse = QGraphicsEllipseItem(node["x"] - 20, node["y"] - 20, 40, 40)
            ellipse.setBrush(QBrush(Qt.white))
            ellipse.setPen(QPen(Qt.black))
            self.scene.addItem(ellipse)
            self.node_map[node["id"]] = ellipse

            text = QGraphicsTextItem(str(node["value"]))
            text.setDefaultTextColor(Qt.black)
            text.setPos(node["x"] - 10, node["y"] - 10)
            self.scene.addItem(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = GraphView(nodes, edges)
    view.show()
    sys.exit(app.exec_())
