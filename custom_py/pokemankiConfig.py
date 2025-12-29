

from aqt import QDialog, QHBoxLayout, QIcon, Qt
from aqt import QVBoxLayout, QLabel, QPushButton
from aqt import mw
from os.path import join, dirname
from aqt import QPixmap,gui_hooks
from aqt.utils import openLink


### このﾌｧｲﾙは使ってない

CHANGE_LOG = "is_change_log_2024_03_26"
IS_RATE_THIS = "is_rate_this"
POKEBALL_PATH = r"pokeball.png"

# CHANGE_LOG = False
# IS_RATE_THIS = False

THE_ADDON_NAME = "Pokemanki Custom"
SHORT_ADDON_NAME = "Pokemanki Gold"
RATE_THIS = None


ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
# ｱﾄﾞｵﾝのURLが数値であるか確認
if (isinstance(ADDON_PACKAGE, (int, float))
    or (isinstance(ADDON_PACKAGE, str)
    and ADDON_PACKAGE.isdigit())):
    RATE_THIS = True

RATE_THIS_URL = f"https://ankiweb.net/shared/review/{ADDON_PACKAGE}"
POPUP_PNG = r"popup_shige.png"


NEW_FEATURE = """
- PokeType button(stats)
    Toggle button for Pokemon picture type.
    (Default is Animation or static image)
"""

RATE_THIS_TEXT = """
[ Changelog : {addon} ]

Shigeyuki :
Hello Pokemon trainer, thank you for using the Pokemanki!
I updated this add-on.
{new_feature}
If you rate this, this feature is activated.
Would you like to add it to feature? Thank you!
""".format(addon=SHORT_ADDON_NAME,new_feature=NEW_FEATURE)





# ------- Rate This PopUp ---------------

def set_gui_hook_rate_this():
    gui_hooks.main_window_did_init.append(change_log_popup)

def change_log_popup(*args,**kwargs):
    try:
        config = mw.addonManager.getConfig(__name__)
        if (config[IS_RATE_THIS] == False
            and config[CHANGE_LOG] == False
            ):

            dialog = CustomDialog()
            if hasattr(dialog, 'exec'):result = dialog.exec() # Qt6
            else:result = dialog.exec_() # Qt5

            if result == QDialog.DialogCode.Accepted:
                open_rate_this_Link(RATE_THIS_URL)
                toggle_rate_this()
            elif  result == QDialog.DialogCode.Rejected:
                toggle_changelog()

    except Exception as e:
        print(e)
        pass

def change_log_popup_B(*args,**kwargs):
    try:
        config = mw.addonManager.getConfig(__name__)
        if (config[IS_RATE_THIS] == False):

            dialog = CustomDialog()
            if hasattr(dialog, 'exec'):result = dialog.exec() # Qt6
            else:result = dialog.exec_() # Qt5

            if result == QDialog.DialogCode.Accepted:
                open_rate_this_Link(RATE_THIS_URL)
                toggle_rate_this()
            elif  result == QDialog.DialogCode.Rejected:
                toggle_changelog()

    except Exception as e:
        print(e)
        pass


class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        addon_path = dirname(__file__)
        icon = QPixmap(join(addon_path, POPUP_PNG))
        layout = QVBoxLayout()

        pokeball_icon = QIcon(join(addon_path, POKEBALL_PATH))
        self.setWindowIcon(pokeball_icon) # QIconオブジェクトを作成します。

        self.setWindowTitle(THE_ADDON_NAME)

        icon_label = QLabel()
        icon_label.setPixmap(icon)

        hbox = QHBoxLayout()

        rate_this_label = QLabel(RATE_THIS_TEXT)
        rate_this_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        hbox.addWidget(icon_label)
        hbox.addWidget(rate_this_label)

        layout.addLayout(hbox)

        button_layout = QHBoxLayout()

        self.yes_button = QPushButton("activate(RateThis)")
        self.yes_button.clicked.connect(self.accept)
        self.yes_button.setFixedWidth(200)
        button_layout.addWidget(self.yes_button)

        self.no_button = QPushButton("No")
        self.no_button.clicked.connect(self.reject)
        self.no_button.setFixedWidth(100)
        button_layout.addWidget(self.no_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

def open_rate_this_Link(url):
    openLink(url)

def toggle_rate_this():
    config = mw.addonManager.getConfig(__name__)
    config[IS_RATE_THIS] = True
    config[CHANGE_LOG] = True
    mw.addonManager.writeConfig(__name__, config)

def toggle_changelog():
    config = mw.addonManager.getConfig(__name__)
    config[CHANGE_LOG] = True
    mw.addonManager.writeConfig(__name__, config)

# -----------------------------------
