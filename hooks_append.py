
from aqt import gui_hooks
from .hooks.menu import reset_menu_globals
from .hooks.overview import reset_overview_globals
from .hooks.message_handler import reset_message_handler_globals
from .utils import reset_utils_global

# globals variables
def reset_main_global_variables():
    
    reset_menu_globals()
    reset_overview_globals()
    reset_message_handler_globals()

# gui hooks

def append_startup_hooks():
    from . import add_button_to_stats_dialog
    gui_hooks.stats_dialog_will_show.append(add_button_to_stats_dialog)


def append_main_hooks():
    from .hooks.deck_browser import replace_gears, deck_browser_open
    from .hooks.overview import overview_open
    from .hooks.initialization import remove_config, delayed_init, reset_global_html
    from .hooks.message_handler import message_handler
    from .hooks.stats import onStatsOpen
    from .hooks.webview_injection import on_webview_inject

    print("  - Registering deck browser hooks")
    gui_hooks.deck_browser_will_render_content.append(replace_gears)
    gui_hooks.deck_browser_will_render_content.append(deck_browser_open)
    
    print("  - Registering addon management hooks")
    gui_hooks.addons_dialog_will_delete_addons.append(remove_config)
    
    print("  - Registering profile hooks")
    gui_hooks.profile_did_open.append(delayed_init)
    
    print("  - Registering stats and overview hooks")
    gui_hooks.stats_dialog_will_show.append(onStatsOpen)
    gui_hooks.overview_will_render_content.append(overview_open)
    
    print("  - Registering message and cleanup hooks")
    gui_hooks.webview_did_receive_js_message.append(message_handler)
    gui_hooks.sync_did_finish.append(reset_global_html)

    print("  - Registering webview injection hooks")
    gui_hooks.webview_did_inject_style_into_page.append(on_webview_inject)


def append_custom_py_hooks():
    from .custom_py.set_js_message import addButtons
    gui_hooks.webview_did_receive_js_message.append(addButtons)


def append_show_pokemon_py_hooks():
    print("  - Registering Pokemon hooks")
    from .helpers.pokemon_helpers import pokemon_show_answer, pokemon_show_question
    from .hooks.study_completion import pokemon_finish_session

    print("    * Registering reviewer hooks")
    gui_hooks.reviewer_will_end.append(pokemon_finish_session)
    gui_hooks.reviewer_did_show_answer.append(pokemon_show_answer)
    gui_hooks.reviewer_did_show_question.append(pokemon_show_question)
    

def all_gui_hooks_append(*args, **kwargs):
    print("🔗 Pokemanki: Registering all GUI hooks")

    # global variables
    print("  - Resetting global variables")
    reset_utils_global()
    reset_main_global_variables()
    
    # gui hooks
    print("  - Registering startup hooks")
    append_startup_hooks()
    print("  - Registering main hooks")
    append_main_hooks()
    print("  - Registering custom py hooks")
    append_custom_py_hooks()
    print("  - Registering show pokemon py hooks")
    append_show_pokemon_py_hooks()
    
    print("✅ Pokemanki: All hooks registered successfully")
