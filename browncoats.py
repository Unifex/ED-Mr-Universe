#!/usr/bin/python

import pprint
import solar_system
import faction

pp = pprint.PrettyPrinter(indent=2)

def gather_faction(name):
    minor_faction_id = faction.get_by_name(name)
    system_ids = faction.get_systems(minor_faction_id)
    for edsm_id in system_ids:
        system = solar_system.get(edsm_id)
        print "##################"
        print "##", system[1]
        factions = solar_system.get_factions(edsm_id)
        for this_faction in factions:
            local_faction = faction.get(this_faction[1])
            print "## * ", local_faction[1], "(", this_faction[3], ") : ", this_faction[2]
        print " "

gather_faction('Browncoats')
