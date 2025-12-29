

from os.path import dirname, join
from aqt import mw, QPushButton
from .path_manager import MoreInfoDialog
from aqt.utils import openLink


def show_more_info():
        from .popup.popup_config import PATRONS_LIST, NEW_FEATURE, OLD_CHANGE_LOG

        change_log_text =  NEW_FEATURE.replace('\n', '<br>')
        change_log_text +=  OLD_CHANGE_LOG.replace('\n', '<br>')
        
        addon_path = dirname(__file__)
        rate_this_path = join(addon_path, "popup", "rate_this_addon.jpg")

        MORE_INFO_TEXT = """
            Made by me for fun
            """

        customBtns = []

        from ..custom_py.popup.button_manager import mini_button

        ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
        RATE_THIS_URL = f"https://ankiweb.net/shared/review/{ADDON_PACKAGE}"
        restart_button = QPushButton("👍️RateThis")
        restart_button.clicked.connect(lambda : openLink(RATE_THIS_URL))
        mini_button(restart_button)
        customBtns.append(restart_button)

        WIKI_URL = f"https://shigeyukey.github.io/shige-addons-wiki/pokemanki-gold.html"
        wiki_button = QPushButton("📖Wiki")
        wiki_button.clicked.connect(lambda : openLink(WIKI_URL))
        mini_button(wiki_button)
        customBtns.append(wiki_button)

        WIKI_REPORT_URL = f"https://shigeyukey.github.io/shige-addons-wiki/pokemanki-gold.html#report"
        report_button = QPushButton("🚨Report")
        report_button.clicked.connect(lambda : openLink(WIKI_REPORT_URL))
        mini_button(report_button)
        customBtns.append(report_button)


        # ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
        # ANKI_WEB_URL = f"https://ankiweb.net/shared/info/{ADDON_PACKAGE}"
        # anki_web_button = QPushButton("🌟AnkiWeb")
        # anki_web_button.clicked.connect(lambda : openLink(ANKI_WEB_URL))
        # customBtns.append(anki_web_button)

        # # REDDIT_URL =  "https://www.reddit.com/user/Shige-yuki"
        # REDDIT_URL = "https://www.reddit.com/r/Anki/comments/1b0eybn/simple_fix_of_broken_addons_for_the_latest_anki/"
        # reddit_url_button = QPushButton("👨‍🚀Reddit")
        # reddit_url_button.clicked.connect(lambda : openLink(REDDIT_URL))
        # customBtns.append(reddit_url_button)

        # GITHUB_URL = "https://github.com/shigeyukey/Pokemanki-Gold/issues"
        # github_button = QPushButton("🐈️Github")
        # github_button.clicked.connect(lambda : openLink(GITHUB_URL))
        # customBtns.append(github_button)

        close_button = QPushButton("Close")
        customBtns.append(close_button)


        MoreInfoDialog(text=MORE_INFO_TEXT, parent=mw, title="Pokemanki Custom", type="shige",textFormat="rich",customBtns=customBtns)
