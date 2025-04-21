#ifndef GUARD_DEBUG_MON_DUMP_H
#define GUARD_DEBUG_MON_DUMP_H

#include "pokemon.h"
#include "gba/types.h"

struct DebugMonDump
{
    u16 species;
    u16 heldItem;
    u8  friendship;
    u16 moves[4];
    u8  pp[4];
    u8  evs[6]; // 0:HP, 1:Atk, 2:Def, 3:Speed, 4:SpAtk, 5:SpDef
};

struct DebugMonDump DumpPartyMonData(struct Pokemon *mon);

#endif // GUARD_DEBUG_MON_DUMP_H