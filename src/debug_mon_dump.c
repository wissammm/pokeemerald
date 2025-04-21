#include "global.h"
#include "debug_mon_dump.h"
#include "pokemon.h"

struct DebugMonDump DumpPartyMonData(struct Pokemon *mon)
{
    struct DebugMonDump dump;
    dump.species     = GetMonData(mon, MON_DATA_SPECIES, NULL);
    dump.heldItem    = GetMonData(mon, MON_DATA_HELD_ITEM, NULL);
    dump.friendship  = GetMonData(mon, MON_DATA_FRIENDSHIP, NULL);
    for (int i = 0; i < 4; i++) {
        dump.moves[i] = GetMonData(mon, MON_DATA_MOVE1 + i, NULL);
        dump.pp[i]    = GetMonData(mon, MON_DATA_PP1 + i, NULL);
    }
    dump.evs[0] = GetMonData(mon, MON_DATA_HP_EV, NULL);
    dump.evs[1] = GetMonData(mon, MON_DATA_ATK_EV, NULL);
    dump.evs[2] = GetMonData(mon, MON_DATA_DEF_EV, NULL);
    dump.evs[3] = GetMonData(mon, MON_DATA_SPEED_EV, NULL);
    dump.evs[4] = GetMonData(mon, MON_DATA_SPATK_EV, NULL);
    dump.evs[5] = GetMonData(mon, MON_DATA_SPDEF_EV, NULL);
    return dump;
}