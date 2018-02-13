#!/usr/bin/python

import settings
from discord_hooks import Webhook
import solar_system
import faction
import time
import pprint

pp = pprint.PrettyPrinter(indent=2)
records = {}

def init(name):
    if name not in records.keys():
        records[name] = {} 
    minor_faction_id = faction.get_by_name(name)
    system_ids = faction.get_systems(minor_faction_id)
    for edsm_id in system_ids:
        system = solar_system.get(edsm_id)
        if system[1] not in records[name].keys():
            records[name][system[1]] = {}
        factions = solar_system.get_factions(edsm_id)
        for this_faction in factions:
            local_faction = faction.get(this_faction[1])
            if local_faction[1] not in records[name][system[1]].keys():
                records[name][system[1]][local_faction[1]] = this_faction[2]

def check_faction(name):
    reports = []
    minor_faction_id = faction.get_by_name(name)
    system_ids = faction.get_systems(minor_faction_id)
    for edsm_id in system_ids:
        system_report = []
        system = solar_system.get(edsm_id)
        if system[1] not in records[name].keys():
            system_report.append('**' + name + '**d influence in ' + system[1] + ' has changed.')
            records[name][system[1]] = {}
        factions = solar_system.get_factions(edsm_id)
        add_report = False
        for this_faction in factions:
            local_faction = faction.get(this_faction[1])
            if local_faction[1] not in records[name][system[1]].keys():
                records[name][system[1]][local_faction[1]] = this_faction[2]
            prev = records[name][system[1]][local_faction[1]]
            current = this_faction[2]
            # Status change.
            if prev < current:
                move = 'increased'
                direction = ':arrow_up_small:'
            else:
                move = 'decreased'
                direction = ':small_red_triangle_down:'
            prev_percent = '{:.1%}'.format(float(prev))
            current_percent = '{:.1%}'.format(float(current))
            if name == local_faction[1] and prev != current:
                # System we are looking at.
                current_system = solar_system.get(edsm_id)
                system_name = current_system[1]

                system_report.insert(0, '**' + local_faction[1] + '** influence in __' + system_name + '__ has ' + move + ' from ' + prev_percent + ' to ' + current_percent)
                records[name][system[1]][local_faction[1]] = this_faction[2]
                add_report = True
            faction_percent = '{:.1%}'.format(float(this_faction[2]))
            system_report.append("* " + local_faction[1] + " (" + this_faction[3] + ") : " + faction_percent + direction)

        if add_report:
            reports.append("\n".join(system_report))
            description = ''
            system_report = []
    if len(reports) > 0:
        post = Webhook(settings.webhook_url,msg="\n\n".join(reports))
        post.post()
        print "\n\n".join(reports)
        print "\n\n"
        reports = []

for this_faction in settings.monitored_factions:
    init(this_faction)

print "###############################"
print "## Initial influences"
pp.pprint(records)
print "###############################"


while True:
    for this_faction in settings.monitored_factions:
       check_faction(this_faction)
       reports = []
    time.sleep(10)
