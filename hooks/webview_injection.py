from aqt import mw
from aqt.webview import AnkiWebView
import os

# Import the display function to generate the Pokemon card HTML
from ..display import _card_html
from ..config import get_synced_conf
from ..pokemon_helpers import get_pokemon_by_id

def on_webview_inject(webview: AnkiWebView) -> None:
    """Hook that fires when CSS is injected into webpages"""
    
    # Check if this is the congratulations page and we have Pokemon data to show
    if webview.page().url().path() == "/congrats":
        print("Detected congrats.html - injecting Pokemon card")
        synced_config_data = get_synced_conf()

        current_pokemon = get_pokemon_by_id(synced_config_data["current_pokemon_id"])
        
        # Generate the Pokemon card HTML
        pokemon_card_html = _card_html(current_pokemon, multi=False, display_deck_or_tag_name=synced_config_data["decks_or_tags"] != "profile")
        
        # Load the CSS content
        addon_dir = os.path.dirname(os.path.dirname(__file__))
        css_path = os.path.join(addon_dir, "pokemanki_css", "view_stats.css")
        css_content = ""
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
        except Exception as e:
            print(f"Could not load CSS: {e}")
            css_content = ""
        
        # Create JavaScript to inject the Pokemon card into congrats page
        js_code = f"""
        {{
            console.log('Injecting Pokemon card into congrats.html');
            
            // Add CSS styles
            const style = document.createElement('style');
            style.textContent = `{css_content}`;
            document.head.appendChild(style);
            
            // Create Pokemon congratulations content
            const pokemonContainer = document.createElement('div');
            pokemonContainer.className = 'pokemon-congrats-container';
            pokemonContainer.innerHTML = `
                <div style="margin: 30px auto; text-align: center; max-width: 600px;">
                    <h2 style="color: #4CAF50; margin-bottom: 20px; font-family: Arial, sans-serif;">🎉 Your Pokemon Gained Experience! 🎉</h2>
                    <div style="display: flex; justify-content: center; margin: 20px 0;">
                        {pokemon_card_html}
                    </div>
                </div>
            `;
            
            // Append to the main content area of congrats page
            const main = document.querySelector('main') || document.body;
            main.appendChild(pokemonContainer);
            
            console.log('Pokemon card successfully injected into congrats page!');
        }}
        """
        
        # Execute the JavaScript
        webview.eval(js_code)
        
