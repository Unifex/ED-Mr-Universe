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
    system_id = solar_system.get_by_name(name)
    system_factions = solar_system.get_factions(system_id)
    for this_faction in system_factions:
        minor_faction = faction.get(this_faction[1])
        if minor_faction[1] not in records[name].keys():
            records[name][minor_faction[1]] = {}
        records[name][minor_faction[1]] = this_faction[2]

def check_system(name):
    reports = []
    system_report = []
    edsm_id = solar_system.get_by_name(name)
    system = solar_system.get(edsm_id)
    if system is None:
        return None
    factions = solar_system.get_factions(edsm_id)
    add_report = False
    for this_faction in factions:
        local_faction = faction.get(this_faction[1])
        if local_faction[1] not in records[name].keys():
            records[name][local_faction[1]] = this_faction[2]
        prev = records[name][local_faction[1]]
        current = this_faction[2]
        if prev is not None:
            # Status change.
            if prev < current:
                move = 'increased'
                direction = ':arrow_up_small:'
            else:
                move = 'decreased'
                direction = ':small_red_triangle_down:'
            # Is this our faction?
            if settings.owners[name] == local_faction[1]:
                home_faction = ':EliteSmile:'
            else:
                home_faction = ''
            prev_percent = '{:.1%}'.format(float(prev))
            current_percent = '{:.1%}'.format(float(current))
            if prev != current:
                # System we are looking at.
                current_system = solar_system.get(edsm_id)
                system_name = current_system[1]
                records[name][local_faction[1]] = this_faction[2]
                add_report = True
                if settings.owners[name] == local_faction[1]:
                    system_report.insert(0, '**' + local_faction[1] + '** influence in __' + system_name + '__ has ' + move + ' from ' + prev_percent + ' to ' + current_percent)
            faction_percent = '{:.1%}'.format(float(this_faction[2]))
            system_report.append("* " + local_faction[1] + home_faction + " (" + this_faction[3] + ") : " + faction_percent + direction)

    if add_report:
        reports.append("\n".join(system_report))
        description = ''
        system_report = []

    if len(reports) > 0:
        post = Webhook(settings.webhook_url_system_monitor,msg="\n\n".join(reports))
        post.post()
        print "\n\n".join(reports)
        print "\n\n"
        reports = []

for this_system in settings.monitored_systems:
    init(this_system)

print "###############################"
print "## Initial influences"
pp.pprint(records)
print "###############################"


while True:
    for this_system in settings.monitored_systems:
       check_system(this_system)
       reports = []
    time.sleep(10)
