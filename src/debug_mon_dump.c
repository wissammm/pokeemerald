#include "global.h"
#include "debug_mon_dump.h"
#include "pokemon.h"

struct DebugMonDump DumpPartyMonData(struct Pokemon *mon)
{
    struct DebugMonDump dump;
    int i;

    dump.species     = GetMonData(mon, MON_DATA_SPECIES, NULL);
    dump.attack      = GetMonData(mon, MON_DATA_ATK, NULL);
    dump.defense     = GetMonData(mon, MON_DATA_DEF, NULL);
    dump.speed       = GetMonData(mon, MON_DATA_SPEED, NULL);
    dump.spAttack    = GetMonData(mon, MON_DATA_SPATK, NULL);
    dump.spDefense   = GetMonData(mon, MON_DATA_SPDEF, NULL);

    for (i = 0; i < MAX_MON_MOVES; i++) {
        dump.moves[i] = GetMonData(mon, MON_DATA_MOVE1 + i, NULL);
        dump.pp[i]    = GetMonData(mon, MON_DATA_PP1 + i, NULL);
    }

    dump.hpIV        = GetMonData(mon, MON_DATA_HP_IV, NULL);
    dump.attackIV    = GetMonData(mon, MON_DATA_ATK_IV, NULL);
    dump.defenseIV   = GetMonData(mon, MON_DATA_DEF_IV, NULL);
    dump.speedIV     = GetMonData(mon, MON_DATA_SPEED_IV, NULL);
    dump.spAttackIV  = GetMonData(mon, MON_DATA_SPATK_IV, NULL);
    dump.spDefenseIV = GetMonData(mon, MON_DATA_SPDEF_IV, NULL);

    dump.isEgg       = GetMonData(mon, MON_DATA_IS_EGG, NULL);
    dump.abilityNum  = GetMonData(mon, MON_DATA_ABILITY_NUM, NULL);
    for (i = 0; i < NUM_BATTLE_STATS; i++)
        dump.statStages[i] = 0;

    dump.ability     = 0;
    dump.type1       = gSpeciesInfo[dump.species].types[0];
    dump.type2       = gSpeciesInfo[dump.species].types[1];

    dump.hp          = GetMonData(mon, MON_DATA_HP, NULL);
    dump.level       = GetMonData(mon, MON_DATA_LEVEL, NULL);
    dump.friendship  = GetMonData(mon, MON_DATA_FRIENDSHIP, NULL);
    dump.maxHP       = GetMonData(mon, MON_DATA_MAX_HP, NULL);
    dump.item        = GetMonData(mon, MON_DATA_HELD_ITEM, NULL);
    dump.ppBonuses   = GetMonData(mon, MON_DATA_PP_BONUSES, NULL);
    dump.personality = GetMonData(mon, MON_DATA_PERSONALITY, NULL);
    dump.status1     = GetMonData(mon, MON_DATA_STATUS, NULL);
    dump.status2     = 0;
    dump.otId        = GetMonData(mon, MON_DATA_OT_ID, NULL);

    return dump;
}


// struct DebugMonDump DumpPartyMonData  (struct Pokemon *mon)
// {
//     struct DebugMonDump dump;
//     int i;

// }