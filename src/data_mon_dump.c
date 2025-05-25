#include "global.h"
#include "data_mon_dump.h"
#include "pokemon.h"

// struct DataMonDump DumpPartyMonData(struct Pokemon *mon)
// {
//     struct DataMonDump dump;
//     int i;
//     dump.isActive    = FALSE;
//     dump.species     = GetMonData(mon, MON_DATA_SPECIES, NULL);
//     dump.attack      = GetMonData(mon, MON_DATA_ATK, NULL);
//     dump.defense     = GetMonData(mon, MON_DATA_DEF, NULL);
//     dump.speed       = GetMonData(mon, MON_DATA_SPEED, NULL);
//     dump.spAttack    = GetMonData(mon, MON_DATA_SPATK, NULL);
//     dump.spDefense   = GetMonData(mon, MON_DATA_SPDEF, NULL);

//     for (i = 0; i < MAX_MON_MOVES; i++) {
//         dump.moves[i] = GetMonData(mon, MON_DATA_MOVE1 + i, NULL);
//         dump.pp[i]    = GetMonData(mon, MON_DATA_PP1 + i, NULL);
//     }

//     dump.hpIV        = GetMonData(mon, MON_DATA_HP_IV, NULL);
//     dump.attackIV    = GetMonData(mon, MON_DATA_ATK_IV, NULL);
//     dump.defenseIV   = GetMonData(mon, MON_DATA_DEF_IV, NULL);
//     dump.speedIV     = GetMonData(mon, MON_DATA_SPEED_IV, NULL);
//     dump.spAttackIV  = GetMonData(mon, MON_DATA_SPATK_IV, NULL);
//     dump.spDefenseIV = GetMonData(mon, MON_DATA_SPDEF_IV, NULL);

//     dump.isEgg       = GetMonData(mon, MON_DATA_IS_EGG, NULL);
//     dump.abilityNum  = GetMonData(mon, MON_DATA_ABILITY_NUM, NULL);
//     for (i = 0; i < NUM_BATTLE_STATS; i++)
//         dump.statStages[i] = 0;

//     dump.ability     = 0;
//     dump.type1       = gSpeciesInfo[dump.species].types[0];
//     dump.type2       = gSpeciesInfo[dump.species].types[1];

//     dump.hp          = GetMonData(mon, MON_DATA_HP, NULL);
//     dump.level       = GetMonData(mon, MON_DATA_LEVEL, NULL);
//     dump.friendship  = GetMonData(mon, MON_DATA_FRIENDSHIP, NULL);
//     dump.maxHP       = GetMonData(mon, MON_DATA_MAX_HP, NULL);
//     dump.item        = GetMonData(mon, MON_DATA_HELD_ITEM, NULL);
//     dump.ppBonuses   = GetMonData(mon, MON_DATA_PP_BONUSES, NULL);
//     dump.personality = GetMonData(mon, MON_DATA_PERSONALITY, NULL);
//     dump.status1     = GetMonData(mon, MON_DATA_STATUS, NULL);
//     dump.status2     = 0;
//     dump.otId        = GetMonData(mon, MON_DATA_OT_ID, NULL);

//     return dump;
// }

/**
 * Dumps Pokémon data into a flat u32 array (1:1 mapping)
 * 
 * Array Index | Corresponding Data
 * ----------- | -----------------
 * [0]         | isActive (bool as u32)
 * [1]         | species (u32)
 * [2]         | attack (u32)  
 * [3]         | defense (u32)
 * [4]         | speed (u32)
 * [5]         | spAttack (u32)
 * [6]         | spDefense (u32)
 * [7]         | move1 (u32)
 * [8]         | move2 (u32)
 * [9]         | move3 (u32)
 * [10]        | move4 (u32)
 * [11]        | hpIV (u32)
 * [12]        | attackIV (u32)
 * [13]        | defenseIV (u32)
 * [14]        | speedIV (u32)
 * [15]        | spAttackIV (u32)
 * [16]        | spDefenseIV (u32)
 * [17]        | isEgg (u32)
 * [18]        | abilityNum (u32)
 * [19]        | ability (u32)
 * [20]        | type1 (u32)
 * [21]        | type2 (u32)
 * [22]        | hp (u32)
 * [23]        | level (u32)
 * [24]        | friendship (u32)
 * [25]        | maxHP (u32)
 * [26]        | item (u32)
 * [27]        | ppBonuses (u32)
 * [28]        | personality (u32)
 * [29]        | status1 (u32)
 * [30]        | status2 (u32)
 * [31]        | otId (u32)
 */
void DumpPartyMonData(struct Pokemon *mon, u32 *dst) {
    int i;
    
    dst[0] = FALSE;  // isActive
    dst[1] = GetMonData(mon, MON_DATA_SPECIES, NULL);
    dst[2] = GetMonData(mon, MON_DATA_ATK, NULL);
    dst[3] = GetMonData(mon, MON_DATA_DEF, NULL);
    dst[4] = GetMonData(mon, MON_DATA_SPEED, NULL);
    dst[5] = GetMonData(mon, MON_DATA_SPATK, NULL);
    dst[6] = GetMonData(mon, MON_DATA_SPDEF, NULL);

    // Moves (sequential indices)
    for (i = 0; i < MAX_MON_MOVES; i++)
        dst[7 + i] = GetMonData(mon, MON_DATA_MOVE1 + i, NULL);

    // IVs
    dst[11] = GetMonData(mon, MON_DATA_HP_IV, NULL);
    dst[12] = GetMonData(mon, MON_DATA_ATK_IV, NULL);
    dst[13] = GetMonData(mon, MON_DATA_DEF_IV, NULL);
    dst[14] = GetMonData(mon, MON_DATA_SPEED_IV, NULL);
    dst[15] = GetMonData(mon, MON_DATA_SPATK_IV, NULL);
    dst[16] = GetMonData(mon, MON_DATA_SPDEF_IV, NULL);

    // Flags
    dst[17] = GetMonData(mon, MON_DATA_IS_EGG, NULL);
    dst[18] = GetMonData(mon, MON_DATA_ABILITY_NUM, NULL);

    // Stats and attributes
    dst[19] = 0;  // ability (placeholder)
    dst[20] = gSpeciesInfo[dst[1]].types[0];  // type1 from species
    dst[21] = gSpeciesInfo[dst[1]].types[1];  // type2 from species
    dst[22] = GetMonData(mon, MON_DATA_HP, NULL);
    dst[23] = GetMonData(mon, MON_DATA_LEVEL, NULL);
    dst[24] = GetMonData(mon, MON_DATA_FRIENDSHIP, NULL);
    dst[25] = GetMonData(mon, MON_DATA_MAX_HP, NULL);
    dst[26] = GetMonData(mon, MON_DATA_HELD_ITEM, NULL);
    dst[27] = GetMonData(mon, MON_DATA_PP_BONUSES, NULL);

    // 32-bit values
    dst[28] = GetMonData(mon, MON_DATA_PERSONALITY, NULL);
    dst[29] = GetMonData(mon, MON_DATA_STATUS, NULL);
    dst[30] = 0;  // status2 (unused)
    dst[31] = GetMonData(mon, MON_DATA_OT_ID, NULL);

    // PP (if needed, though moves were already stored)
    for (i = 0; i < MAX_MON_MOVES; i++)
        dst[32 + i] = GetMonData(mon, MON_DATA_PP1 + i, NULL);
}
