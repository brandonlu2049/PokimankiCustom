from aqt import mw
from aqt.utils import tooltip

from ..helpers.pokemon_helpers import get_pokemon_by_id, set_pokemon_by_id

def save_changes(pokemon_id: str, nickname: str, everstone: bool, megastone: bool, alolan: bool):
    """Save all changes made to the pokemon"""
    # Update nickname
    pokemon_data = get_pokemon_by_id(pokemon_id)
    pokemon_data["nickname"] = nickname
    
    # Ensure items dict exists (for backwards compatibility with old data)
    if "items" not in pokemon_data:
        pokemon_data["items"] = {"everstone": False, "megastone": False, "alolan": False}
    
    # Update items
    pokemon_data["items"]["everstone"] = everstone
    pokemon_data["items"]["megastone"] = megastone
    pokemon_data["items"]["alolan"] = alolan
    set_pokemon_by_id(pokemon_id, pokemon_data)
    
    tooltip("Changes saved!")

    from ..hooks.initialization import reset_global_html
    reset_global_html()
    mw.reset()
    # Force refresh the deck browser/overview webview if visible
    if mw.state == "deckBrowser":
        mw.deckBrowser.refresh()
    elif mw.state == "overview":
        mw.overview.refresh()

