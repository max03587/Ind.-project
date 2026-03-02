import sys, ctypes
from PySide6.QtWidgets import QApplication, QGraphicsPixmapItem, QGraphicsItem, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtGui import QBrush, QColor, QPixmap, QIcon
from PySide6.QtCore import QSize, Qt


current_player = "white"
SQUARE_SIZE = 80

class ChessPiece(QGraphicsPixmapItem):
    def __init__(self, image, position, piece_color, piece_type, board_positions):
        super().__init__()
        self.color = piece_color
        self.type = piece_type
        self.board_positions = board_positions
        
        pixmap = QPixmap(image).scaled(SQUARE_SIZE, SQUARE_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)
        self.setPos(position[0], position[1])
        
        self.setFlag(QGraphicsItem.ItemIsMovable, self.color == current_player)
        self._initial_pos = self.pos()
        self._start_drag_pos = None

    def get_piece_at(self, x, y):
        for item in self.scene().items():
            if isinstance(item, ChessPiece) and item != self:
                if item.pos().x() == x and item.pos().y() == y:
                    return item
        return None

    def is_path_clear(self, start_pos, end_pos):
        dx = int((end_pos[0] - start_pos[0]) / SQUARE_SIZE)
        dy = int((end_pos[1] - start_pos[1]) / SQUARE_SIZE)
        
        step_x = (dx // abs(dx)) if dx != 0 else 0
        step_y = (dy // abs(dy)) if dy != 0 else 0
        
        curr_x, curr_y = start_pos[0] + step_x * SQUARE_SIZE, start_pos[1] + step_y * SQUARE_SIZE
        while (curr_x, curr_y) != end_pos:
            if self.get_piece_at(curr_x, curr_y):
                return False
            curr_x += step_x * SQUARE_SIZE
            curr_y += step_y * SQUARE_SIZE
        return True

    def is_valid_move(self, start_pos, end_pos):
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        dx = int((end_x - start_x) / SQUARE_SIZE)
        dy = int((end_y - start_y) / SQUARE_SIZE)
        
        target_piece = self.get_piece_at(end_x, end_y)
        

        if target_piece and target_piece.color == self.color:
            return False


        if self.type == "king":
            return abs(dx) <= 1 and abs(dy) <= 1


        if self.type == "rook":
            if dx == 0 or dy == 0:
                return self.is_path_clear(start_pos, end_pos)
            return False


        if self.type == "bishop":
            if abs(dx) == abs(dy):
                return self.is_path_clear(start_pos, end_pos)
            return False


        if self.type == "queen":
            if dx == 0 or dy == 0 or abs(dx) == abs(dy):
                return self.is_path_clear(start_pos, end_pos)
            return False


        if self.type == "knight":
            return (abs(dx) == 2 and abs(dy) == 1) or (abs(dx) == 1 and abs(dy) == 2)


        if self.type == "pawn":
            direction = -1 if self.color == "white" else 1 
            start_row = 560 if self.color == "white" else 80
            

            if dx == 0 and not target_piece:
                if dy == direction: return True
                if dy == 2 * direction and start_y == start_row:
                    return not self.get_piece_at(start_x, start_y + direction * SQUARE_SIZE)
            

            if abs(dx) == 1 and dy == direction and target_piece:
                return True
            return False

        return False

    def mousePressEvent(self, event):
        if self.color != current_player:
            event.ignore()
            return
        self._start_drag_pos = self.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.color != current_player: return


        new_x = round(self.pos().x() / SQUARE_SIZE) * SQUARE_SIZE
        new_y = round(self.pos().y() / SQUARE_SIZE) * SQUARE_SIZE
        closest_pos = (new_x, new_y)


        if (closest_pos in self.board_positions and 
            self.is_valid_move((self._initial_pos.x(), self._initial_pos.y()), closest_pos)):
            

            target_piece = self.get_piece_at(new_x, new_y)
            if target_piece:
                self.scene().removeItem(target_piece)

            self.setPos(new_x, new_y)
            self._initial_pos = self.pos()
            self.switch_turn()
        else:
            self.setPos(self._initial_pos)

        super().mouseReleaseEvent(event)

    def switch_turn(self):
        global current_player
        current_player = "black" if current_player == "white" else "white"
        for item in self.scene().items():
            if isinstance(item, ChessPiece):
                item.setFlag(QGraphicsItem.ItemIsMovable, item.color == current_player)


class Main_window(QMainWindow):
    def __init__(self, scene):
        super().__init__()
        self.setWindowTitle("Шахматы")
        self.setFixedSize(680, 680)
        view = QGraphicsView(scene)
        self.setCentralWidget(view)

app = QApplication(sys.argv)
scene = QGraphicsScene(0, 0, 640, 640)


board_positions = []
for row in range(8):
    for col in range(8):
        x, y = col * SQUARE_SIZE, row * SQUARE_SIZE
        board_positions.append((x, y))
        rect = QGraphicsRectItem(x, y, SQUARE_SIZE, SQUARE_SIZE)
        rect.setBrush(QColor("white") if (row + col) % 2 == 0 else QColor("darkGray"))
        scene.addItem(rect)

def add_piece(img, pos, color, p_type):
    piece = ChessPiece(img, pos, color, p_type, board_positions)
    scene.addItem(piece)


add_piece("Project/picture/Wlad.png", (0, 560), "white", "rook")
add_piece("Project/picture/Wknight.png", (80, 560), "white", "knight")
add_piece("Project/picture/Wbishop.png", (160, 560), "white", "bishop")
add_piece("Project/picture/Wquin.png", (240, 560), "white", "queen")
add_piece("Project/picture/Wking.png", (320, 560), "white", "king")
add_piece("Project/picture/Wbishop.png", (400, 560), "white", "bishop")
add_piece("Project/picture/Wknight.png", (480, 560), "white", "knight")
add_piece("Project/picture/Wlad.png", (560, 560), "white", "rook")

for i in range(8):
    add_piece("Project/picture/Wpeshka.png", (i * 80, 480), "white", "pawn")


add_piece("Project/picture/Blad.png", (0, 0), "black", "rook")
add_piece("Project/picture/Bknight.png", (80, 0), "black", "knight")
add_piece("Project/picture/Bbishop.png", (160, 0), "black", "bishop")
add_piece("Project/picture/Bquin.png", (240, 0), "black", "queen")
add_piece("Project/picture/Bking.png", (320, 0), "black", "king")
add_piece("Project/picture/Bbishop.png", (400, 0), "black", "bishop")
add_piece("Project/picture/Bknight.png", (480, 0), "black", "knight")
add_piece("Project/picture/Blad.png", (560, 0), "black", "rook")
for i in range(8):
    add_piece("Project/picture/Bpeshka.png", (i * 80, 80), "black", "pawn")

window = Main_window(scene)
window.show()
sys.exit(app.exec())