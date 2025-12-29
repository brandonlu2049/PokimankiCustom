

import os
import random
from aqt import (QHBoxLayout, QLabel, QPixmap, QPushButton, QResizeEvent, QSizePolicy, QTabWidget,
                QTextBrowser, QTextEdit, QTimer, QUrl, QVBoxLayout, QWebEngineView, QWidget,QIcon,QMessageBox,QDialog,Qt,qconnect)
from os.path import join, dirname
from aqt import mw

POKEBALL_PATH = "pokeball.png"
PROFESSOR_01 = ["ProfessorOak01.png", "ProfessorElm01.png", "ProfessorRowan01.png",
                "Pokemon_Breeder_m_OD_01.png","Pokemon_Breeder_f_OD_01.png",
                "Nurse_OD_01.png","PC_Nurse_IV_OD_01.png","PC_Nurse_OD_01.png",
                ]
PROFESSOR_02 = ["ProfessorOak02.png", "ProfessorElm02.png", "ProfessorRowan02.png"]
PROFESSOR_ONRY = ["ProfessorOak01.png", "ProfessorElm01.png", "ProfessorRowan01.png"]



POPUP_PNG = r"popup_shige.png"

addon_package = mw.addonManager.addonFromModule(__name__)
mediafolder = f"/_addons/{addon_package}/custom_py/Trainer_100"

addon_path = dirname(__file__)
trainer_path = join(addon_path,"Trainer_100")
all_files = os.listdir(trainer_path)

selected_files = random.sample(all_files, 4)
random_trainer_image = [os.path.join(mediafolder, filename) for filename in selected_files]

FIRST_POKEMON = "starter_pokemon"




def get_icon_path(name, format="icon"):
    """ pix,icon """
    addon_path = dirname(__file__)
    icon_path = join(addon_path, name)

    if format == "pix":
        return QPixmap(icon_path)
    else:
        return QIcon(icon_path)


class CustomWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(get_icon_path(POKEBALL_PATH)))


class CustomMessageBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(get_icon_path(POKEBALL_PATH)))

        layout = QVBoxLayout()
        self.icon_path = get_icon_path(random.choice(PROFESSOR_01), "pix")
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QPixmap(self.icon_path))
        hbox = QHBoxLayout()

        hbox.addWidget(self.icon_label)

        self.text_label = QTextBrowser()
        self.text_label.setReadOnly(True)
        self.text_label.setOpenExternalLinks(True)
        self.text_label.setMinimumWidth(400)
        self.text_label.setMinimumHeight(100)
        hbox.addWidget(self.text_label)

        # self.text_label = QLabel()
        # self.text_label.setWordWrap(False)
        # self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        # hbox.addWidget(self.text_label)

        self.hbox2 = QHBoxLayout()
        self.hbox2.addStretch(1)
        # self.display_image_below_text("Ditto")
        # self.display_image_below_text("Ditto")
        # self.display_image_below_text("Ditto")

        self.custom_widget = QWidget()
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(self.hbox2)
        self.custom_widget.setLayout(vbox)
        layout = self.layout() # Get default layout
        layout.addWidget(self.custom_widget, 0, 1) # Add custom widget



    def setText(self, text):
        self.text_label.setText(text)

    def change_icon_path(self):
        icon = QPixmap(get_icon_path(random.choice(PROFESSOR_02), "pix"))
        self.icon_label.setPixmap(icon)
        # if hasattr(resetwindow, 'change_icon_path'): resetwindow.change_icon_path() # ｶｽﾀﾑ

    def change_icon_path_professors(self):
        icon = QPixmap(get_icon_path(random.choice(PROFESSOR_ONRY), "pix"))
        self.icon_label.setPixmap(icon)
        # if hasattr(msgbox, 'change_icon_path'): msgbox.change_icon_path_professors() # ｶｽﾀﾑ

    def display_image_below_text(self,text):
        addon_path = dirname(__file__)
        pokemon_images = join(addon_path,FIRST_POKEMON, f"{text}.png")
        pixmap = QPixmap(pokemon_images)
        scaled_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image_label = QLabel()  # Create a new QLabel for each image
        image_label.setPixmap(scaled_pixmap)
        self.hbox2.addWidget(image_label)
        # if hasattr(msgbox, 'change_icon_path'): msgbox.display_image_below_text() # ｶｽﾀﾑ


class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(get_icon_path(POKEBALL_PATH)))



class InfoDialog(QDialog):
    def __init__(
        self,
        text: str,
        parent: None = None,
        help: None = None,
        type: str = "info",
        title: str = "Anki",
        textFormat: None = None,
        customBtns: None = None,
    ):
        super().__init__(parent)

        layout = QVBoxLayout()

        if type == "warning" or type == "critical":
            icon = QPixmap(get_icon_path(random.choice(PROFESSOR_02), "pix"))
        elif type == "shige":
            icon = QPixmap(get_icon_path(POPUP_PNG,"pix"))
        else:
            icon = QPixmap(get_icon_path(random.choice(PROFESSOR_01), "pix"))

        icon_label = QLabel()
        icon_label.setPixmap(icon)

        text_edit = QTextBrowser()
        text_edit.setReadOnly(True)
        text_edit.setOpenExternalLinks(True)
        # text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        if "<img src=" in text:
            textFormat = "rich"
            text.replace("\n","<br>")


        if textFormat == "plain":
            text_edit.setPlainText(text)
        elif textFormat == "rich":
            text_edit.setHtml("<html><body>" + text + "</body></html>")
        elif textFormat == "markdown":
            text_edit.setHtml("<html><body><pre>" + text + "</pre></body></html>")
        else:
            text_edit.setPlainText(text)

        hbox = QHBoxLayout()

        hbox.addWidget(icon_label)
        hbox.addWidget(text_edit)

        layout.addLayout(hbox)

        if customBtns:
            if customBtns:
                btn_layout = QHBoxLayout()
                btn_layout.addStretch(1)
                for btn in customBtns:
                    btn_layout.addWidget(btn)
                    btn.clicked.connect(self.accept)
                layout.addLayout(btn_layout)
        else:
            btn = QPushButton("OK")
            btn.setFixedWidth(100)
            btn.clicked.connect(self.accept)

            btn_layout = QHBoxLayout()
            btn_layout.addStretch(1)
            btn_layout.addWidget(btn)

            layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(get_icon_path(POKEBALL_PATH)))

        # content_height = text_edit.document().size().height() +100

        def get_content_height():
            content_height = int(text_edit.document().size().height() +100)
            self.resize(500, content_height if content_height < 400 else 400)

        # process the event loop once to get the height of the HTML content.
        QTimer.singleShot(0, get_content_height)

        # self.resize(500, content_height if content_height<400 else 400)
        # self.resize(500, self.size().height()if self.size().height()<400 else 400)
        # self.exec()
        self.show()



class MoreInfoDialog(QDialog):
    def __init__(
        self,
        text: str,
        parent: None = None,
        help: None = None,
        type: str = "info",
        title: str = "Anki",
        textFormat: None = None,
        customBtns: None = None,
    ):
        super().__init__(parent)

        layout = QVBoxLayout()

        if type == "warning" or type == "critical":
            icon = QPixmap(get_icon_path(random.choice(PROFESSOR_02), "pix"))
        elif type == "shige":
            icon = QPixmap(get_icon_path(POPUP_PNG,"pix"))
        else:
            icon = QPixmap(get_icon_path(random.choice(PROFESSOR_01), "pix"))

        icon_label = QLabel()
        icon_label.setPixmap(icon)

        text_edit = QTextBrowser()
        text_edit.setReadOnly(True)
        text_edit.setOpenExternalLinks(True)
        # text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        if textFormat == "plain":
            text_edit.setPlainText(text)
        elif textFormat == "rich":
            text_edit.setHtml("<html><body>" + text + "</body></html>")
        elif textFormat == "markdown":
            text_edit.setHtml("<html><body><pre>" + text + "</pre></body></html>")
        else:
            text_edit.setPlainText(text)

        tab_widget = QTabWidget()

        info_widget = QWidget()
        info_layout = QHBoxLayout()
        info_layout.addWidget(icon_label)
        info_layout.addWidget(text_edit)
        info_widget.setLayout(info_layout)

        tab_widget.addTab(info_widget, "MoreInfo")

        from ..custom_py.popup.endroll.endroll import add_credit_tab
        
        add_credit_tab(self, tab_widget)

        layout.addWidget(tab_widget)

        if customBtns:
            if customBtns:
                btn_layout = QHBoxLayout()
                btn_layout.addStretch(1)
                for btn in customBtns:
                    btn_layout.addWidget(btn)
                    btn.clicked.connect(self.accept)
                layout.addLayout(btn_layout)
        else:
            btn = QPushButton("OK")
            btn.setFixedWidth(100)
            btn.clicked.connect(self.accept)

            btn_layout = QHBoxLayout()
            btn_layout.addStretch(1)
            btn_layout.addWidget(btn)

            layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(get_icon_path(POKEBALL_PATH)))

        # self.resize(500, self.size().height()if self.size().height()<300 else 300)

        self.adjust_self_size()
        self.show()

    def adjust_self_size(self):
        # min_size = self.layout().minimumSize()
        # self.resize(min_size.width(), min_size.height())
        # Width: 546, Height: 472
        PATREON_LABEL_WIDTH = 546
        WIDGET_HEIGHT = 472
        self.resize(PATREON_LABEL_WIDTH, WIDGET_HEIGHT)


    def resizeEvent(self, event:"QResizeEvent"):
        size = event.size()
        print(f"Width: {size.width()}, Height: {size.height()}")
        super().resizeEvent(event)


# class InfoDialog(QMessageBox):
#     def __init__(
#         self,
#         text: str,
#         parent: None = None,
#         help: None = None,
#         type: str = "info",
#         title: str = "Anki",
#         textFormat: None = None,
#         customBtns: None = None,
#     ):
#         parent_widget: QWidget
#         if parent is None:
#             parent_widget = aqt.mw.app.activeWindow() or aqt.mw
#         else:
#             parent_widget = parent
#         super().__init__(parent_widget)

#         if type == "warning":
#             icon = QMessageBox.Icon.Warning
#         elif type == "critical":
#             icon = QMessageBox.Icon.Critical
#         else:
#             icon = QMessageBox.Icon.Information
#         self.setIcon(icon)
#         self.setWindowIcon(QIcon(get_icon_path(POKEBALL_PATH)))

#         if textFormat == "plain":
#             self.setTextFormat(Qt.TextFormat.PlainText)
#         elif textFormat == "rich":
#             self.setTextFormat(Qt.TextFormat.RichText)
#         elif textFormat == "markdown":
#             self.setTextFormat(Qt.TextFormat.MarkdownText)
#         elif textFormat is not None:
#             raise Exception("unexpected textFormat type")

#         self.setText(text)
#         self.setWindowTitle(title)

#         if customBtns:
#             default = None
#             for btn in customBtns:
#                 b = self.addButton(btn)
#                 if not default:
#                     default = b
#             self.setDefaultButton(default)
#         else:
#             b = self.addButton(QMessageBox.StandardButton.Ok)
#             b.setDefault(True)

#         # if help is not None:
#         #     b = self.addButton(QMessageBox.StandardButton.Help)
#         #     qconnect(b.clicked, lambda: openHelp(help))
#         #     b.setAutoDefault(False)

#         self.exec()