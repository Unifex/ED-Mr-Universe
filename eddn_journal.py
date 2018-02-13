#!/usr/bin/python

import settings
import sqlite3
import pprint

db = sqlite3.connect(settings.db_path)
pp = pprint.PrettyPrinter(indent=2)
debug = False

def process(data):
    print data['header']['uploaderID']
    if 'message' in data.keys():
        if debug:
            print data['message'].keys()
        if 'Factions' in data['message'].keys():
            if debug or process_minor_factions(data['message']['Factions']):
                update_system_minor_factions(data['message'])

# Should we process the source of this collection of minor factions?
def process_minor_factions(data):
    for faction in data:
        if faction['Name'] in settings.monitored_factions:
            return True
    return False

def update_system_minor_factions(data):
    system = data['StarSystem']
    minor_factions = data['Factions'] 
    validate_system(data)
    if debug:
        print "## Minor Factions"
        pp.pprint(minor_factions)

def validate_system(data):
    if debug:
        print "## StarSystem"
        pp.pprint(data)
    # Do we have this system?
    c = db.cursor()
    if debug:
        pp.pprint(data['StarSystem'])
    edsm_id = c.execute('SELECT edsm_id FROM systems WHERE name = ?', (data['StarSystem'],)).fetchone()
    if edsm_id == None:
        edsm_id = save_system(data)
    else:
        edsm_id = edsm_id[0]
    print data['StarSystem']
    for faction in data['Factions']:
        faction_id = fetch_faction_id(faction['Name'], data['Factions'])
        vals = [
                edsm_id,
                faction_id,
                faction['Influence'],
                faction['FactionState'],
                ]
        sql = 'INSERT OR REPLACE INTO system_minor_factions VALUES (?,?,?,?)'
        pp.pprint(vals)
        c.execute(sql, vals)
    db.commit()

def fetch_faction_id(name, factions):
    c = db.cursor()
    faction_id = c.execute('SELECT id FROM minor_factions WHERE name = ?', (name,)).fetchone()
    if faction_id == None:
        for faction in factions:
            if faction['Name'] == name:
                faction_id = save_faction(faction)
    else:
        return faction_id[0]
    

def save_faction(data):
    c = db.cursor()
    sql = "INSERT INTO minor_factions (id, name, government) VALUES (?,?,?);"
    faction_id = next_faction_id()
    vals = [
        faction_id,
        data['Name'],
        data['Government'],
        ]
    c.execute(sql, vals)
    db.commit()

def next_faction_id():
    c = db.cursor()
    ret = c.execute('SELECT MAX(id) FROM minor_factions;').fetchone()[0]
    ret += 1
    return ret

def save_system(data):
    c = db.cursor()
    sql = "INSERT INTO systems VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
    edsm_id = next_system_id()
    faction_id = fetch_faction_id(data['SystemFaction'], data['Factions'])
    vals = [
            edsm_id,
            data['StarSystem'],
            data['SystemGovernment'],
            data['StarPos'][0],
            data['StarPos'][1],
            data['StarPos'][2],
            data['Population'],
            data['SystemSecurity'],
            data['SystemEconomy'],
            data['timestamp'],
            faction_id,
            ]
    c.execute(sql, vals)
    db.commit()

def next_system_id():
    c = db.cursor()
    ret = c.execute('SELECT MAX(edsm_id) FROM systems;').fetchone()[0]
    ret += 1
    return ret
