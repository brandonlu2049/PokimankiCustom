import random
import uuid

# for test, not used.

def test_tag_matching():
    # ﾃｽﾄﾃﾞｰﾀの準備
    note_tags = [
        "EIJIRO::level-01", 
        "EIJIRO::level-01::03::04", 
        "level-01::EIJIRO",
        "PIKACHU::level-02",
        "PIKACHU::level-02::05::06",
        "level-02::PIKACHU",
        "BULBASAUR::level-03",
        "BULBASAUR::level-03::07::08",
        "level-03::BULBASAUR"
    ]
    pokemon_date = {
        "tags": [
            {"id": str(uuid.uuid4()), "name": "Charmander", "deck": "EIJIRO::level-01", "level": 0.65, "nickname": None},
            {"id": str(uuid.uuid4()), "name": "Wartortle", "deck": "EIJIRO", "level": 34.51, "nickname": None},
            {"id": str(uuid.uuid4()), "name": "Pikachu", "deck": "PIKACHU::level-02::05::06", "level": 12.34, "nickname": None},
            {"id": str(uuid.uuid4()), "name": "Bulbasaur", "deck": "BULBASAUR::level-03", "level": 23.45, "nickname": None},
            {"id": str(uuid.uuid4()), "name": "Squirtle", "deck": "SQUIRTLE::level-04", "level": 45.67, "nickname": None},
            {"id": str(uuid.uuid4()), "name": "Jigglypuff", "deck": "JIGGLYPUFF::level-05", "level": 56.78, "nickname": None},
            {"id": str(uuid.uuid4()), "name": "Meowth", "deck": "MEOWTH::level-06", "level": 67.89, "nickname": None},
            {"id": str(uuid.uuid4()), "name": "Psyduck", "deck": "PSYDUCK::level-07", "level": 78.90, "nickname": None},
            {"id": str(uuid.uuid4()), "name": "Machop", "deck": "MACHOP::level-08", "level": 89.01, "nickname": None},
            {"id": str(uuid.uuid4()), "name": "Geodude", "deck": "GEODUDE::level-09", "level": 90.12, "nickname": None}
        ]
    }
    decks_or_tags = "tags"

    # 実行部分
    if decks_or_tags == "tags":
        pokemons = pokemon_date["tags"]
        matched_pokemons = []

        for tagname in note_tags:
            tag_parts = tagname.split("::")
            for pokemon in pokemons:
                pokemon_tag_parts = pokemon["deck"].split("::")
                if tag_parts[:len(pokemon_tag_parts)] == pokemon_tag_parts:
                    name, level = pokemon["name"], pokemon["level"]
                    if (name, level) not in matched_pokemons:
                        matched_pokemons.append((name, level, pokemon["deck"].count("::")))
                        print(f"Match found: Name: {name}, Level: {level}, Tag: {pokemon['deck']}")


        # :: の数が最も多いﾀｸﾞのﾎﾟｹﾓﾝをﾌｨﾙﾀﾘﾝｸﾞ
        if matched_pokemons:
            max_colons = max(matched_pokemons, key=lambda x: x[2])[2]
            filtered_pokemons = [p for p in matched_pokemons if p[2] == max_colons]
            selected_pokemon = random.choice(filtered_pokemons)
            print(f"Selected Pokemon: Name: {selected_pokemon[0]}, Level: {selected_pokemon[1]}, Tag: {selected_pokemon[2]}")  # ﾃﾞﾊﾞｯｸﾞ用のprint文

    # 結果の確認
    # print(f"Matched Pokemons: {matched_pokemons}")


# ﾃｽﾄの実行
test_tag_matching()