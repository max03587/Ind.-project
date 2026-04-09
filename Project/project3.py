import sys
from PySide6.QtWidgets import QApplication, QGraphicsPixmapItem, QGraphicsItem, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QMainWindow, QGraphicsDropShadowEffect, QVBoxLayout, QPushButton, QWidget, QLabel, QStackedWidget
from PySide6.QtGui import QColor, QPixmap, QFont
from PySide6.QtCore import Qt, QPointF

# Глобальные переменные
current_player = "white"
last_pawn_double_move = None
SQUARE_SIZE = 80

class ChessPiece(QGraphicsPixmapItem):
    def __init__(self, image, position, piece_color, piece_type, board_positions):
        super().__init__()
        self.color = piece_color
        self.type = piece_type
        self.board_positions = board_positions
        self.image_path = image
        
        self.update_appearance(image)
        self.setPos(position[0], position[1])
        
        self.setFlag(QGraphicsItem.ItemIsMovable, self.color == current_player)
        self._initial_pos = self.pos()

    def update_appearance(self, image_path):
        pixmap = QPixmap(image_path).scaled(SQUARE_SIZE, SQUARE_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)

    def get_piece_at(self, x, y):
        for item in self.scene().items():
            if isinstance(item, ChessPiece) and item.isVisible():
                if abs(item.pos().x() - x) < 5 and abs(item.pos().y() - y) < 5:
                    return item
        return None

    def get_king(self, color):
        for item in self.scene().items():
            if isinstance(item, ChessPiece) and item.type == "king" and item.color == color:
                return item
        return None

    def is_square_attacked(self, x, y, attacker_color):
        for item in self.scene().items():
            if isinstance(item, ChessPiece) and item.color == attacker_color and item.isVisible():
                if item.is_valid_move((item.pos().x(), item.pos().y()), (x, y), ignore_check_logic=True):
                    return True
        return False

    def is_path_clear(self, start_pos, end_pos):
        dx = int(round((end_pos[0] - start_pos[0]) / SQUARE_SIZE))
        dy = int(round((end_pos[1] - start_pos[1]) / SQUARE_SIZE))
        step_x = (dx // abs(dx)) if dx != 0 else 0
        step_y = (dy // abs(dy)) if dy != 0 else 0
        
        curr_x, curr_y = start_pos[0] + step_x * SQUARE_SIZE, start_pos[1] + step_y * SQUARE_SIZE
        while abs(curr_x - end_pos[0]) > 5 or abs(curr_y - end_pos[1]) > 5:
            if self.get_piece_at(curr_x, curr_y):
                return False
            curr_x += step_x * SQUARE_SIZE
            curr_y += step_y * SQUARE_SIZE
        return True

    def is_valid_move(self, start_pos, end_pos, ignore_check_logic=False):
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        dx = int(round((end_x - start_x) / SQUARE_SIZE))
        dy = int(round((end_y - start_y) / SQUARE_SIZE))
        
        if dx == 0 and dy == 0: return False
        target_piece = self.get_piece_at(end_x, end_y)
        if target_piece and target_piece.color == self.color:
            return False

        possible = False
        if self.type == "king":
            possible = abs(dx) <= 1 and abs(dy) <= 1
        elif self.type == "rook":
            possible = (dx == 0 or dy == 0) and self.is_path_clear(start_pos, end_pos)
        elif self.type == "bishop":
            possible = abs(dx) == abs(dy) and self.is_path_clear(start_pos, end_pos)
        elif self.type == "queen":
            possible = (dx == 0 or dy == 0 or abs(dx) == abs(dy)) and self.is_path_clear(start_pos, end_pos)
        elif self.type == "knight":
            possible = (abs(dx) == 2 and abs(dy) == 1) or (abs(dx) == 1 and abs(dy) == 2)
        elif self.type == "pawn":
            direction = -1 if self.color == "white" else 1 
            start_row = 480 if self.color == "white" else 80
            if dx == 0 and dy == direction and not target_piece:
                possible = True
            elif dx == 0 and dy == 2 * direction and start_y == start_row:
                if not self.get_piece_at(start_x, start_y + direction * SQUARE_SIZE) and not target_piece:
                    possible = True
            elif abs(dx) == 1 and dy == direction:
                if target_piece and target_piece.color != self.color:
                    possible = True
                elif not target_piece and last_pawn_double_move:
                    lp_pos = last_pawn_double_move.pos()
                    if abs(lp_pos.x() - end_x) < 5 and abs(lp_pos.y() - start_y) < 5:
                        possible = True

        if not possible: return False
        if not ignore_check_logic:
            return self.is_move_safe(start_pos, end_pos)
        return True

    def is_move_safe(self, start_pos, end_pos):
        original_pos = self.pos()
        target_piece = self.get_piece_at(end_pos[0], end_pos[1])
        if target_piece: target_piece.setVisible(False)
        self.setPos(end_pos[0], end_pos[1])
        king = self.get_king(self.color)
        safe = True
        if king:
            enemy_color = "black" if self.color == "white" else "white"
            if self.is_square_attacked(king.pos().x(), king.pos().y(), enemy_color):
                safe = False
        self.setPos(original_pos)
        if target_piece: target_piece.setVisible(True)
        return safe

    def promote_pawn_if_needed(self):
        if self.type == "pawn":
            promotion_row = 0 if self.color == "white" else 560
            if abs(self.pos().y() - promotion_row) < 5:
                self.type = "queen"
                new_img = "Project/picture/Wquin.png" if self.color == "white" else "Project/picture/Bquin.png"
                self.update_appearance(new_img)

    def check_for_check_display(self):
        for color in ["white", "black"]:
            king = self.get_king(color)
            if not king: continue
            enemy_color = "black" if color == "white" else "white"
            if self.is_square_attacked(king.pos().x(), king.pos().y(), enemy_color):
                glow = QGraphicsDropShadowEffect()
                glow.setBlurRadius(25); glow.setColor(QColor("red")); glow.setOffset(0)
                king.setGraphicsEffect(glow)
            else:
                king.setGraphicsEffect(None)

    def is_checkmate(self, color):
        for item in self.scene().items():
            if isinstance(item, ChessPiece) and item.color == color:
                current_p = (item.pos().x(), item.pos().y())
                for board_p in self.board_positions:
                    if item.is_valid_move(current_p, board_p):
                        return False
        return True

    def mousePressEvent(self, event):
        if self.color != current_player:
            event.ignore(); return
        self._initial_pos = self.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        global current_player, last_pawn_double_move
        if self.color != current_player: return

        new_x = round(self.pos().x() / SQUARE_SIZE) * SQUARE_SIZE
        new_y = round(self.pos().y() / SQUARE_SIZE) * SQUARE_SIZE
        closest_pos = (new_x, new_y)
        old_pos = (self._initial_pos.x(), self._initial_pos.y())

        if closest_pos in self.board_positions and self.is_valid_move(old_pos, closest_pos):
            target_piece = self.get_piece_at(new_x, new_y)
            if self.type == "pawn" and not target_piece and abs(new_x - old_pos[0]) == SQUARE_SIZE:
                if last_pawn_double_move: self.scene().removeItem(last_pawn_double_move)

            if target_piece: self.scene().removeItem(target_piece)

            if self.type == "pawn" and abs(new_y - old_pos[1]) == 2 * SQUARE_SIZE:
                last_pawn_double_move = self
            else:
                last_pawn_double_move = None 

            self.setPos(new_x, new_y)
            self.promote_pawn_if_needed()
            self._initial_pos = self.pos()
            self.check_for_check_display()
            self.switch_turn()
            
            if self.is_checkmate(current_player):
                print(f"МАТ! Победили {'черные' if current_player == 'black' else 'белые'}")
        else:
            self.setPos(self._initial_pos)
        super().mouseReleaseEvent(event)

    def switch_turn(self):
        global current_player
        current_player = "black" if current_player == "white" else "white"
        for item in self.scene().items():
            if isinstance(item, ChessPiece):
                item.setFlag(QGraphicsItem.ItemIsMovable, item.color == current_player)

class StartMenu(QWidget):
    """Виджет начального меню"""
    def __init__(self, start_callback, exit_callback):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("CHESS ")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setStyleSheet("margin-bottom: 50px; color: #333;")
        
        btn_start = QPushButton("Начать игру")
        btn_start.setFixedSize(250, 60)
        btn_start.setFont(QFont("Arial", 14))
        btn_start.clicked.connect(start_callback)
        btn_start.setStyleSheet("background-color: #779556; color: white; border-radius: 10px;")

        btn_exit = QPushButton("Выход")
        btn_exit.setFixedSize(250, 60)
        btn_exit.setFont(QFont("Arial", 14))
        btn_exit.clicked.connect(exit_callback)
        btn_exit.setStyleSheet("background-color: #d32f2f; color: white; border-radius: 10px; margin-top: 10px;")

        layout.addWidget(title)
        layout.addWidget(btn_start)
        layout.addWidget(btn_exit)
        self.setLayout(layout)

class Main_window(QMainWindow):
    def __init__(self, scene):
        super().__init__()
        self.setWindowTitle("Шахматы")
        self.setFixedSize(680, 680)
        view = QGraphicsView(scene)
        self.setCentralWidget(view)

# --- Инициализация ---
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

# Расстановка фигур... (аналогично предыдущему коду)
# Белые
add_piece("Project/picture/Wlad.png", (0, 560), "white", "rook")
add_piece("Project/picture/Wknight.png", (80, 560), "white", "knight")
add_piece("Project/picture/Wbishop.png", (160, 560), "white", "bishop")
add_piece("Project/picture/Wquin.png", (240, 560), "white", "queen")
add_piece("Project/picture/Wking.png", (320, 560), "white", "king")
add_piece("Project/picture/Wbishop.png", (400, 560), "white", "bishop")
add_piece("Project/picture/Wknight.png", (480, 560), "white", "knight")
add_piece("Project/picture/Wlad.png", (560, 560), "white", "rook")
for i in range(8): add_piece("Project/picture/Wpeshka.png", (i * 80, 480), "white", "pawn")
# Черные
add_piece("Project/picture/Blad.png", (0, 0), "black", "rook")
add_piece("Project/picture/Bknight.png", (80, 0), "black", "knight")
add_piece("Project/picture/Bbishop.png", (160, 0), "black", "bishop")
add_piece("Project/picture/Bquin.png", (240, 0), "black", "queen")
add_piece("Project/picture/Bking.png", (320, 0), "black", "king")
add_piece("Project/picture/Bbishop.png", (400, 0), "black", "bishop")
add_piece("Project/picture/Bknight.png", (480, 0), "black", "knight")
add_piece("Project/picture/Blad.png", (560, 0), "black", "rook")
for i in range(8): add_piece("Project/picture/Bpeshka.png", (i * 80, 80), "black", "pawn")

window = Main_window(scene)
window.show()
sys.exit(app.exec())