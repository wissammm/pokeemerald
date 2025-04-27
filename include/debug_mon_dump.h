#ifndef GUARD_DEBUG_MON_DUMP_H
#define GUARD_DEBUG_MON_DUMP_H

#include "pokemon.h"
#include "gba/types.h"

struct DebugMonDump
{
    u16 species;
    u16 attack;
    u16 defense;
    u16 speed;
    u16 spAttack;
    u16 spDefense;
    u16 moves[MAX_MON_MOVES];
    u32 hpIV:5;
    u32 attackIV:5;
    u32 defenseIV:5;
    u32 speedIV:5;
    u32 spAttackIV:5;
    u32 spDefenseIV:5;
    u32 isEgg:1;
    u32 abilityNum:1;
    s8 statStages[NUM_BATTLE_STATS];
    u8 ability;
    u8 type1;
    u8 type2;
    u8 pp[MAX_MON_MOVES];
    u16 hp;
    u8 level;
    u8 friendship;
    u16 maxHP;
    u16 item;
    u8 ppBonuses;
    u32 personality;
    u32 status1;
    u32 status2;
    u32 otId;
};

struct DebugMonDump DumpPartyMonData(struct Pokemon *mon);

#endif // GUARD_DEBUG_MON_DUMP_H