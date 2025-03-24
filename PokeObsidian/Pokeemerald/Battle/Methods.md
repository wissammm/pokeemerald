## Starting methods

### Sprites
#### void CB2_InitBattle(void)
id:597904
The `AllocateBattleSpritesData` function ensures that the necessary memory is allocated for storing battle sprites data and Pokémon sprites graphics data. It checks if the memory has already been allocated (by checking if the pointers are `NULL`) and allocates the memory if needed, initializing it to zero.

This function is typically called at the beginning of a battle to set up the required data structures for handling battle sprites and graphics.