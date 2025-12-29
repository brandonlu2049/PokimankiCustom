

from aqt import QAction, QDialog, QHBoxLayout, QIcon, QMenu, QResizeEvent, QTabWidget, QTextBrowser, QWidget, Qt, qconnect
from aqt import QVBoxLayout, QLabel, QPushButton
from aqt import mw
from os.path import join, dirname
from aqt import QPixmap,gui_hooks
from aqt.utils import openLink
from .change_log import OLD_CHANGE_LOG #🟢
from .endroll.endroll import add_credit_tab
from .button_manager import mini_button

CHANGE_LOG = "is_change_log"
# CHANGE_LOG_DAY = "2024-06-23-"
# CHANGE_LOG_DAY = "2024-10-14c"
# CHANGE_LOG_DAY = "2025-02-08b"
# CHANGE_LOG_DAY = "2025-02-08d"
# CHANGE_LOG_DAY = "2025-04-22a"
CHANGE_LOG_DAY = "2025-06-08a" #🟢

POKEBALL_PATH = r"popup_icon.png"
POPUP_PNG = r"popup_shige.png"

# popup-size
# mini-pupup
SIZE_MINI_WIDTH = 642
SIZE_MINI_HEIGHT = 360
# Width: 642, Height: 360


# Large-popup
SIZE_BIG_WIDTH = 600
SIZE_BIG_HEIGHT = 500


THE_ADDON_NAME = "🎮️Pokemanki Custom - Raising Pokemon with Anki (Forked by Me)"
SHORT_ADDON_NAME = "🎮️Pokemanki Custom"



ANKI_WEB_URL = ""
RATE_THIS_URL = ""
ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
# ｱﾄﾞｵﾝのURLが数値であるか確認
if (isinstance(ADDON_PACKAGE, (int, float))
    or (isinstance(ADDON_PACKAGE, str)
    and ADDON_PACKAGE.isdigit())):
    ANKI_WEB_URL = f"https://ankiweb.net/shared/info/{ADDON_PACKAGE}"
    RATE_THIS_URL = f"https://ankiweb.net/shared/review/{ADDON_PACKAGE}"


NEW_FEATURE = """
[1] 1st version
"""
UPDATE_TEXT = "I updated this Add-on."

CHANGE_LOG_TEXT = """\
added stuff
"""

def set_gui_hook_change_log():
    gui_hooks.main_window_did_init.append(change_log_popup)
    # gui_hooks.main_window_did_init.append(add_config_button)

def change_log_popup(*args,**kwargs):
    try:
        config = mw.addonManager.getConfig(__name__)
        # if (config[IS_RATE_THIS] == False and config[CHANGE_LOG] == False):
        if (config.get(CHANGE_LOG, False) != CHANGE_LOG_DAY):

            dialog = CustomDialog(mw, CHANGE_LOG_TEXT, size_mini=True)
            dialog.show()
            update_changelog()

    except Exception as e:
        print(e)
        pass


class CustomDialog(QDialog):
    def __init__(self, parent=None,change_log_text=CHANGE_LOG_TEXT,more_button=False,size_mini=False):
        super().__init__(parent)

        addon_path = dirname(__file__)
        icon = QPixmap(join(addon_path, POPUP_PNG))
        layout = QVBoxLayout()
        if size_mini:
            self.resize(SIZE_MINI_WIDTH, SIZE_MINI_HEIGHT)
        else:
            self.resize(SIZE_BIG_WIDTH, SIZE_BIG_HEIGHT)

        pokeball_icon = QIcon(join(addon_path, POKEBALL_PATH))
        self.setWindowIcon(pokeball_icon)

        self.setWindowTitle(THE_ADDON_NAME)

        tab_widget = QTabWidget()
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)


        icon_label = QLabel()
        icon_label.setPixmap(icon)

        hbox = QHBoxLayout()

        change_log_label = QTextBrowser()
        change_log_label.setReadOnly(True)
        change_log_label.setOpenExternalLinks(True)

        change_log_label.setPlainText(change_log_text)

        hbox.addWidget(icon_label)
        hbox.addWidget(change_log_label)

        tab_layout.addLayout(hbox)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.no_button = QPushButton("OK (Close)")
        self.no_button.clicked.connect(self.close)
        self.no_button.setFixedWidth(120)

        button_layout.addWidget(self.yes_button)
        button_layout.addWidget(self.report_button)
        button_layout.addWidget(self.no_button)

        tab_widget.addTab(tab, "Change Log")
        add_credit_tab(self, tab_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(tab_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)


    def resizeEvent(self, event:"QResizeEvent"):
        size = event.size()
        print(f"Width: {size.width()}, Height: {size.height()}")
        super().resizeEvent(event)

def update_changelog():
    config = mw.addonManager.getConfig(__name__)
    config[CHANGE_LOG] = CHANGE_LOG_DAY
    mw.addonManager.writeConfig(__name__, config)

