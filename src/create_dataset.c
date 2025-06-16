#include "create_dataset.h"

#include "global.h"
#include "pokemon.h"

static u8 MoveAlreadyExists(u32 *moves, u32 move, int numMoves) {
    for (int i = 0; i < numMoves; i++) {
        if (moves[i] == move) {
            return TRUE;
        }
    }
    return FALSE;
}

// Helper function to add a move to the array if it's not already there
static int AddMove(u32 *moves, u32 move, int numMoves) {
    if (!MoveAlreadyExists(moves, move, numMoves)) {
        moves[numMoves] = move;
        return numMoves + 1;
    }
    return numMoves;
}

int RetrivesAllMoves(u16 species, u32 *moves) {
    if (species >= NUM_SPECIES) {
        DebugPrintf("Invalid species ID: %d\n", species);
        return 0 ;
    }

    int numMoves = 0; 

    // // 1. Level-Up Moves
    // const u16 *learnset = gLevelUpLearnsets[species];
    // for (int i = 0; learnset[i] != LEVEL_UP_END; i++) {
    //     u16 levelMove = learnset[i];
    //     u16 level = levelMove >> 9;
    //     u16 move = levelMove & 0x1FF;

    //     numMoves = AddMove(moves, move, numMoves);
    //     if (numMoves >= MAX_MOVES) break;
    // }

    // u32 tutorMovesBitfield = sTutorLearnsets[species];
    // for (int i = 0; i < 30; i++) {
    //     if (tutorMovesBitfield & (1 << i)) {
    //         numMoves = AddMove(moves, gTutorMoves[i], numMoves);
    //         if (numMoves >= MAX_MOVES) break;
    //     }
    // }


    // while (numMoves < MAX_MOVES) {
    //     moves[numMoves] = 0;
    //     numMoves++;
    // }
    return numMoves;
}

void PrintPokemonData(u16 species){
    if (species >= NUM_SPECIES) {
        DebugPrintf("Invalid species ID: %d\n", species);
        return;
    }
    const struct SpeciesInfo *info = &gSpeciesInfo[species];
    DebugPrintf("Species: %d\n", species);
    DebugPrintf("baseHP: %d\n", info->baseHP);
    DebugPrintf("baseAttack: %d\n", info->baseAttack);
    DebugPrintf("baseDefense: %d\n", info->baseDefense);
    DebugPrintf("baseSpeed: %d\n", info->baseSpeed);
    DebugPrintf("baseSpAttack: %d\n", info->baseSpAttack);
    DebugPrintf("baseSpDefense: %d\n", info->baseSpDefense);
    DebugPrintf("type0: %d\n", info->types[0]);
    DebugPrintf("type1: %d\n", info->types[1]);
    u32 moves[MAX_MOVES] = {0};
    
}