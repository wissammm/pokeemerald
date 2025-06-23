#include "global.h"
#include "data_mon_dump.h"
#include "pokemon.h"


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

    // abilityNum (plus de isEgg)
    dst[17] = GetMonData(mon, MON_DATA_ABILITY_NUM, NULL);

    // Stats and attributes
    dst[18] = 0;  // ability (placeholder)
    dst[19] = gSpeciesInfo[dst[1]].types[0];  // type1 from species
    dst[20] = gSpeciesInfo[dst[1]].types[1];  // type2 from species
    dst[21] = GetMonData(mon, MON_DATA_HP, NULL);
    dst[22] = GetMonData(mon, MON_DATA_LEVEL, NULL);
    dst[23] = GetMonData(mon, MON_DATA_FRIENDSHIP, NULL);
    dst[24] = GetMonData(mon, MON_DATA_MAX_HP, NULL);
    dst[25] = GetMonData(mon, MON_DATA_HELD_ITEM, NULL);
    dst[26] = GetMonData(mon, MON_DATA_PP_BONUSES, NULL);
    dst[27] = GetMonData(mon, MON_DATA_PERSONALITY, NULL);
    dst[28] = GetMonData(mon, MON_DATA_STATUS, NULL);
    dst[29] = 0;// Status2
    dst[30] = 0;// Status3
    // PP (if needed, though moves were already stored)
    for (i = 0; i < MAX_MON_MOVES; i++)
        dst[31 + i] = GetMonData(mon, MON_DATA_PP1 + i, NULL);
}