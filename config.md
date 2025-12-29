###  `align_cards` [string]:  
1. `wrap` to start a new row if Pokémon cards don't fit on one line  
1. `hscroll` to keep them on one line and add a horizontal scroll bar  
1. `scrollbox` Scroll box height is fixed to the number of pixels of maxheight  
    1. `max_height_px` Sets the scroll box height  

### Number of deck name splits
Number from the end of the name of the deck to be displayed.  
For example,  
1. MasterDeck::Subdeck::Sub1::Sub2::Sub3
2. "Number of deck name splits": 1
3. Sub3

### Generations
If you change the generation configs from `true` to `false`, you may need to reset the pokemons or an error may occur.