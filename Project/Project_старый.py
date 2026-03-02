import sys,ctypes
from PySide6.QtWidgets import QApplication, QGraphicsPixmapItem,QGraphicsItem , QGraphicsScene, QGraphicsView, QGraphicsRectItem, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtGui import QBrush, QColor, QPixmap,QIcon
from PySide6.QtCore import QSize

current_player = "white"
Wfigurs = []
Bfigurs = []

class Main_window(QMainWindow):
    def __init__(self, scene):
        super().__init__()
        self.setWindowTitle("Шахматы")
        self.setFixedSize(QSize(680, 680))
        self.setCentralWidget(central_widget)
        self.scene = scene


app = QApplication(sys.argv)
central_widget = QWidget()
layout = QVBoxLayout()
central_widget.setLayout(layout)


scene = QGraphicsScene()


class fig_item(QGraphicsPixmapItem):
    def __init__(self, image, position, width, height,board_positions,color,type):
        super().__init__()
        self.color = color
        pixmap = QPixmap(image).scaled(width, height)
        if pixmap.isNull():
            print(f"Не удалось загрузить изображение {image}")
        self.setPixmap(pixmap)
        self.setPos(*position)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        #self.setFlag(QGraphicsItem.ItemIsSelectable,True)
        self._start_pos = None
        self.board_positions = board_positions
        self._initial_pos = self.pos()

    def check_collision(self, new_x, new_y, exclude_item=None):
        for item in self.scene().items():
            if item is exclude_item:
                continue
            if hasattr(item, 'boundingRect'):
                rect = item.boundingRect()
                item_pos = item.scenePos()
                item_x = item_pos.x()
                item_y = item_pos.y()
                if (abs(new_x - item_x) < rect.width() and
                    abs(new_y - item_y) < rect.height()):
                    return True
        return False 
       
    def is_valid_move(self, start_pos, end_pos):
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        dx = int((end_x - start_x) / square_size) 
        dy = int((end_y - start_y) / square_size)  

        if self.type == "king":
            return abs(dx) <= 1 and abs(dy) <= 1 and (dx != 0 or dy != 0)

        if self.type == "lad":  
            return (dx == 0 or dy == 0) and (dx != 0 or dy != 0)

        if self.type == "pawn":
            direction = 1 if self.color == "white" else -1
            if dx == 0 and dy == direction:
                return True
            if dx == 0 and dy == 2 * direction and ((start_y == 480 and self.color == "white") or (start_y == 80 and self.color == "black")):
                return True
            return False

        if self.type == "quin":  
            if (abs(dx) == abs(dy) and dx != 0) or ((dx == 0) != (dy == 0) and (dx != 0 or dy != 0)):
                return True
            #return False
        #return True
               
    def mousePressEvent(self, event):
        self._start_pos = event.scenePos()
        self._initial_pos = self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._start_pos is not None:
            new_pos = event.scenePos()
            delta = new_pos - self._start_pos
            self.setPos(self.pos() + delta)
            self._start_pos = new_pos
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        global current_player
        new_x = self.pos().x()
        new_y = self.pos().y()

        collision = self.check_collision(new_x, new_y, exclude_item=self)
        
        if collision:
            self.setPos(self._initial_pos)
            return
        else:
            closest_pos = self.closest_board_position()
            self.setPos(*closest_pos)
        
        if (closest_pos[0] == self._initial_pos.x() and
        closest_pos[1] == self._initial_pos.y()):
            super().mouseReleaseEvent(event)
            return
        
        closest_pos = self.closest_board_position()

        if not self.is_valid_move((self._initial_pos.x(), self._initial_pos.y()), closest_pos):
            self.setPos(self._initial_pos)
            return
        
        if current_player == 'white':
            current_player = 'black'

        if self.color != current_player:
            for i in Wfigurs:
                i.setFlag(QGraphicsItem.ItemIsSelectable,False)
                i.setFlag(QGraphicsItem.ItemIsMovable,False)
            for i in Bfigurs:
                i.setFlag(QGraphicsItem.ItemIsMovable,True)  

        super().mouseReleaseEvent(event)
        
        
    def closest_board_position(self):
        min_distance = float('inf')
        closest_point = None
        current_x = self.scenePos().x()
        current_y = self.scenePos().y()

       
        for pos in self.board_positions:
            dx = pos[0] - current_x
            dy = pos[1] - current_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_point = pos
        return closest_point


class Bfig_item(QGraphicsPixmapItem):
    def __init__(self, image, position, width, height,board_positions,color,type):
        super().__init__()
        self.color = color
        pixmap = QPixmap(image).scaled(width, height)
        if pixmap.isNull():
            print(f"Не удалось загрузить изображение {image}")
        self.setPixmap(pixmap)
        self.setPos(*position)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        #self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self._start_pos = None
        self.board_positions = board_positions
        self._initial_pos = self.pos()

    def check_collision(self, new_x, new_y, exclude_item=None):
        for item in self.scene().items():
            if item is exclude_item:
                continue
            if hasattr(item, 'boundingRect'):
                rect = item.boundingRect()
                item_pos = item.scenePos()
                item_x = item_pos.x()
                item_y = item_pos.y()
                if (abs(new_x - item_x) < rect.width() and
                    abs(new_y - item_y) < rect.height()):
                    return True
        return False    
    
    def mousePressEvent(self, event):
        self._start_pos = event.scenePos()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self._start_pos is not None:
            new_pos = event.scenePos()
            delta = new_pos - self._start_pos
            self.setPos(self.pos() + delta)
            self._start_pos = new_pos
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        global current_player
        new_x = self.pos().x()
        new_y = self.pos().y()

        collision = self.check_collision(new_x, new_y, exclude_item=self)
        if collision:
            self.setPos(self._initial_pos)
            return
        else:
            closest_pos = self.closest_board_position()
            self.setPos(*closest_pos)

        if (closest_pos[0] == self._initial_pos.x() and
        closest_pos[1] == self._initial_pos.y()):
            super().mouseReleaseEvent(event)
            return
        
        if current_player == 'black':
            current_player = 'white'

        if self.color != current_player:
            for i in Bfigurs:
                i.setFlag(QGraphicsItem.ItemIsSelectable,False)
                i.setFlag(QGraphicsItem.ItemIsMovable,False)
            for i in Wfigurs:
                i.setFlag(QGraphicsItem.ItemIsMovable,True)


        closest_pos = self.closest_board_position()
        self.setPos(closest_pos[0], closest_pos[1])
        super().mouseReleaseEvent(event)
        
        
    def closest_board_position(self):
        min_distance = float('inf')
        closest_point = None
        current_x = self.scenePos().x()
        current_y = self.scenePos().y()

        
        for pos in self.board_positions:
            dx = pos[0] - current_x
            dy = pos[1] - current_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_point = pos
        return closest_point



board_positions = []
square_size = 80
for row in range(8):
    for col in range(8):
        x = col * square_size
        y = row * square_size
        board_positions.append((x, y))
        rect_item = QGraphicsRectItem(x, y, square_size, square_size)
        color = QColor("white") if (row + col) % 2 == 0 else QColor("darkGray")
        rect_item.setBrush(QBrush(color))
        scene.addItem(rect_item)

Wking = fig_item("Project\picture\Wking.png", position=(320, 560), width=80, height=80,board_positions= board_positions,color= "white",type="king")
Wfigurs.append(Wking)

Bking = Bfig_item("Project\picture\Bking.png", position=(320, 0), width=80, height=80,board_positions= board_positions,color= "black",type="king")
Bfigurs.append(Bking)

Wquin = fig_item("Project\picture\Wquin.png", position=(240, 560), width=80, height=80,board_positions= board_positions,color= "white",type="quin")
Wfigurs.append(Wquin)

Bquin = Bfig_item("Project\picture\Bquin.png", position=(240, 0), width=80, height=80,board_positions= board_positions,color= "black",type="quin")
Bfigurs.append(Bquin)

W1lad = fig_item("Project\picture\Wlad.png", position=(0, 560), width=70, height=70,board_positions= board_positions,color= "white",type="lad")
Wfigurs.append(W1lad)

W2lad = fig_item("Project\picture\Wlad.png", position=(560, 560), width=70, height=70,board_positions= board_positions,color= "white",type="lad")
Wfigurs.append(W2lad)

B1lad = Bfig_item("Project\picture\Blad.png", position=(0, 0), width=70, height=70,board_positions= board_positions,color= "black",type="lad")
Bfigurs.append(B1lad)
B2lad = Bfig_item("Project\picture\Blad.png", position=(560, 0), width=70, height=70,board_positions= board_positions,color= "black",type="lad")
Bfigurs.append(B2lad)


W1knight = fig_item("Project\picture\Wknight.png", position=(80, 560), width=70, height=70,board_positions= board_positions,color= "white",type="knight")
Wfigurs.append(W1knight)

W2knight = fig_item("Project\picture\Wknight.png", position=(480, 560), width=70, height=70,board_positions= board_positions,color= "white",type="knight")
Wfigurs.append(W2knight)

B1knight = Bfig_item("Project\picture\Bknight.png", position=(80, 0), width=70, height=70,board_positions= board_positions,color= "black",type="knight")
Bfigurs.append(B1knight)
B2knight = Bfig_item("Project\picture\Bknight.png", position=(480, 0), width=70, height=70,board_positions= board_positions,color= "black",type="knight")
Bfigurs.append(B2knight)

W1bishop = fig_item("Project\picture\Wbishop.png", position=(160, 560), width=70, height=70,board_positions= board_positions,color= "white",type="bishop")
Wfigurs.append(W1bishop)

W2bishop = fig_item("Project\picture\Wbishop.png", position=(400, 560), width=70, height=70,board_positions= board_positions,color= "white",type="bishop")
Wfigurs.append(W2bishop)

B1bishop = Bfig_item("Project\picture\Bbishop.png", position=(160, 0), width=70, height=70,board_positions= board_positions,color= "black",type="bishop")
Bfigurs.append(B1bishop)
B2bishop = Bfig_item("Project\picture\Bbishop.png", position=(400, 0), width=70, height=70,board_positions= board_positions,color= "black",type="bishop")
Bfigurs.append(B2bishop)

W1peshka = fig_item("Project\picture\Wpeshka.png", position=(0, 480), width=70, height=70,board_positions= board_positions,color= "white",type="pawn")
Wfigurs.append(W1peshka)
W2peshka = fig_item("Project\picture\Wpeshka.png", position=(80, 480), width=70, height=70,board_positions= board_positions,color= "white",type="pawn")
Wfigurs.append(W2peshka)
W3peshka = fig_item("Project\picture\Wpeshka.png", position=(160, 480), width=70, height=70,board_positions= board_positions,color= "white",type="pawn")
Wfigurs.append(W3peshka)
W4peshka = fig_item("Project\picture\Wpeshka.png", position=(240, 480), width=70, height=70,board_positions= board_positions,color= "white",type="pawn")
Wfigurs.append(W4peshka)
W5peshka = fig_item("Project\picture\Wpeshka.png", position=(320, 480), width=70, height=70,board_positions= board_positions,color= "white",type="pawn")
Wfigurs.append(W5peshka)
W6peshka = fig_item("Project\picture\Wpeshka.png", position=(400, 480), width=70, height=70,board_positions= board_positions,color= "white",type="pawn")
Wfigurs.append(W6peshka)
W7peshka = fig_item("Project\picture\Wpeshka.png", position=(480, 480), width=70, height=70,board_positions= board_positions,color= "white",type="pawn")
Wfigurs.append(W7peshka)
W8peshka = fig_item("Project\picture\Wpeshka.png", position=(560, 480), width=70, height=70,board_positions= board_positions,color= "white",type="pawn")
Wfigurs.append(W8peshka)

B1peshka = Bfig_item("Project\picture\Bpeshka.png", position=(0, 80), width=70, height=70,board_positions= board_positions,color= "black",type="pawn")
Bfigurs.append(B1peshka)
B2peshka = Bfig_item("Project\picture\Bpeshka.png", position=(80, 80), width=70, height=70,board_positions= board_positions,color= "black",type="pawn")
Bfigurs.append(B2peshka)
B3peshka = Bfig_item("Project\picture\Bpeshka.png", position=(160, 80), width=70, height=70,board_positions= board_positions,color= "black",type="pawn")
Bfigurs.append(B3peshka)
B4peshka = Bfig_item("Project\picture\Bpeshka.png", position=(240, 80), width=70, height=70,board_positions= board_positions,color= "black",type="pawn")
Bfigurs.append(B4peshka)
B5peshka = Bfig_item("Project\picture\Bpeshka.png", position=(320, 80), width=70, height=70,board_positions= board_positions,color= "black",type="pawn")
Bfigurs.append(B5peshka)
B6peshka = Bfig_item("Project\picture\Bpeshka.png", position=(400, 80), width=70, height=70,board_positions= board_positions,color= "black",type="pawn")
Bfigurs.append(B6peshka)
B7peshka = Bfig_item("Project\picture\Bpeshka.png", position=(480, 80), width=70, height=70,board_positions= board_positions,color= "black",type="pawn")
Bfigurs.append(B7peshka)
B8peshka = Bfig_item("Project\picture\Bpeshka.png", position=(560, 80), width=70, height=70,board_positions= board_positions,color= "black",type="pawn")
Bfigurs.append(B8peshka)

scene.addItem(Bking)
scene.addItem(Wking)

scene.addItem(Wquin)
scene.addItem(Bquin)

scene.addItem(W1lad)
scene.addItem(W2lad)
scene.addItem(B1lad)
scene.addItem(B2lad)

scene.addItem(B1knight)
scene.addItem(B2knight)
scene.addItem(W1knight)
scene.addItem(W2knight)

scene.addItem(W1bishop)
scene.addItem(W2bishop)
scene.addItem(B1bishop)
scene.addItem(B2bishop)

scene.addItem(W1peshka)
scene.addItem(W2peshka)
scene.addItem(W3peshka)
scene.addItem(W4peshka)
scene.addItem(W5peshka)
scene.addItem(W6peshka)
scene.addItem(W7peshka)
scene.addItem(W8peshka)

scene.addItem(B1peshka)
scene.addItem(B2peshka)
scene.addItem(B3peshka)
scene.addItem(B4peshka)
scene.addItem(B5peshka)
scene.addItem(B6peshka)
scene.addItem(B7peshka)
scene.addItem(B8peshka)

scene.setBackgroundBrush(QColor("gray"))





view = QGraphicsView(scene)
layout.addWidget(view)

if __name__ == "__main__":
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "mycompany.myproduct.texteditor"
        )

app.setWindowIcon(QIcon("Project\picture\chess_queen_icon_198474.ico"))
window = Main_window(scene)
window.show()

sys.exit(app.exec())