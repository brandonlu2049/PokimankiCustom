

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QIcon
from os.path import join, dirname

POKEBALL_PNG = "pokeball.png"

def get_icon_path(name):
    addon_path = dirname(__file__)
    icon_path = join(addon_path, name)
    return icon_path

pokeball_path = get_icon_path(POKEBALL_PNG)

app = QApplication([])
window = QWidget()

window.setWindowIcon(QIcon(pokeball_path)) # Add a Pokeball icon

window.show()
app.exec()



# from os.path import join, dirname
# from aqt import QWidget, QIcon, QPixmap

# def get_icon_path(name):
#     addon_path = dirname(__file__)
#     icon_path = join(addon_path, name)
#     return QPixmap(icon_path)

# POKEBALL_PNG = "pokeball.png"

# pokeball_path = get_icon_path(POKEBALL_PNG)



class CustomWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(get_icon_path(pokeball_path)))