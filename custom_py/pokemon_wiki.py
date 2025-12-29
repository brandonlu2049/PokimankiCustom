

import os
from aqt import QDialog, QLabel, QMenu, QWebEnginePage, QWebEngineSettings, QVBoxLayout, QWebEngineView, QWidget, Qt, mw, QUrl, QSize
from aqt import QWebEngineProfile, QTimer, QPixmap, QIcon
from aqt.webview import AnkiWebView



class ResizableWebView(QDialog):
    def __init__(self,url):
        super().__init__()
        self.setWindowTitle("Pokedex")
        self.resize(QSize(1000, 700))

        addon_path = os.path.dirname(__file__)
        pokeball_icon = QIcon(os.path.join(addon_path, "pokeball.png"))
        self.setWindowIcon(pokeball_icon) # QIconオブジェクトを作成します。



        # ---------- Cookie monster ---------------
        self.cookie_profile = QWebEngineProfile("shige_pokemanki_profile")
        # profile = QWebEngineProfile.defaultProfile() # ﾃﾞﾌｫﾙﾄのﾌﾟﾛﾌｧｲﾙ名
        self.cookie_profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        # browser_storage_folder =  os.path.join(os.path.dirname(__file__), "user_files","cookie_data")
        base_dir = os.path.dirname(os.path.dirname(__file__))
        browser_storage_folder = os.path.join(base_dir, "user_files", "cookie_data")
        if not  os.path.exists(browser_storage_folder):
            os.makedirs(browser_storage_folder)
        self.cookie_profile.setPersistentStoragePath(browser_storage_folder)
        # ---------- Cookie monster ---------------



        self.web = CustomWebEngineView(self)

        # self.web = MyWebPage(self.cookie_profile, self.web)
        webpage = QWebEnginePage(self.cookie_profile, self.web) # Cookie monster
        self.web.setPage(webpage)
        # self.web.setPage(MyWebPage(self.web))

        # # ----------------------------------
        # self.grey_widget = QWidget()
        # # self.grey_widget.setStyleSheet("background-color: grey;")
        # addon_path = os.path.dirname(__file__)
        # icon_path = os.path.join(addon_path , "NowLoading.png")
        # pixmap = QPixmap(icon_path)
        # self.label = QLabel(self.grey_widget)
        # self.label.setPixmap(pixmap)
        # self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # layout = QVBoxLayout(self.grey_widget)
        # layout.addWidget(self.label)
        # self.grey_widget.setLayout(layout)
        # # ----------------------------------





        self.web.setUrl(QUrl(url))
        # self.web.loadFinished.connect(self.show_webview)


        # interceptor = WebEngineUrlRequestInterceptor()
        # self.web.page().profile().setUrlRequestInterceptor(interceptor)



        settings = self.web.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.web)
        # layout.addWidget(self.grey_widget)

        layout.setContentsMargins(1, 1, 1, 1)

        self.setLayout(layout)


    # def hide_webview(self):
    #     self.grey_widget.setVisible(True)
    #     self.web.setVisible(False)

    # def show_webview(self):
    #     self.grey_widget.setVisible(False)
    #     self.web.setVisible(True)


    # def loadfinish(self):
    #     self.show()
    #     self.raise_()

# def pokemon_web_view(url):
#     mw.search_pokemanki_dialog = ResizableWebView(url)
#     mw.search_pokemanki_dialog.show()

def pokemon_web_view(url):
    if hasattr(mw, 'search_pokemanki_dialog'):
        mw.search_pokemanki_dialog.web.setUrl(QUrl(url))
        QTimer.singleShot(0,mw.search_pokemanki_dialog.show)
        QTimer.singleShot(0,mw.search_pokemanki_dialog.raise_)

    else:
        mw.search_pokemanki_dialog = ResizableWebView(url)
        # QTimer.singleShot(0,mw.search_pokemanki_dialog.hide_webview)
        QTimer.singleShot(0,mw.search_pokemanki_dialog.show)
        QTimer.singleShot(0,mw.search_pokemanki_dialog.raise_)



class CustomWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        if not self.pageAction(QWebEnginePage.WebAction.Copy).isEnabled():
            if self.pageAction(QWebEnginePage.WebAction.Back).isEnabled():
                menu.addAction(self.pageAction(QWebEnginePage.WebAction.Back))
            if self.pageAction(QWebEnginePage.WebAction.Forward).isEnabled():
                menu.addAction(self.pageAction(QWebEnginePage.WebAction.Forward))
            if self.pageAction(QWebEnginePage.WebAction.Reload).isEnabled():
                menu.addAction(self.pageAction(QWebEnginePage.WebAction.Reload))

        if self.pageAction(QWebEnginePage.WebAction.Copy).isEnabled():
            menu.addAction(self.pageAction(QWebEnginePage.WebAction.Copy))

        try:menu.exec(event.globalPos())
        except:menu.exec_(event.globalPos())



class MyWebPage(QWebEnginePage):
    # ﾊﾟｿｺﾝのﾃﾞﾌｫﾙﾄのﾌﾞﾗｳｻﾞで開かれてしまう場合､
    # QWebEnginePageのcreateWindow関数をｵｰﾊﾞｰﾗｲﾄﾞする必要がある
    def createWindow(self, QWebEnginePage_WebWindowType):
        new_webview = AnkiWebView(title="My Web Page")
        new_webview.setPage(MyWebPage(new_webview))
        return new_webview.page()