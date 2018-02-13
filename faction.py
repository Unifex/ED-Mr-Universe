#!/usr/bin/python

import settings
import sqlite3
import pprint

db = sqlite3.connect(settings.db_path)
pp = pprint.PrettyPrinter(indent=2)

def get(id):
    sql = 'SELECT * FROM minor_factions WHERE id = ?;'
    c = db.cursor()
    ret = c.execute(sql, (id,)).fetchone()
    return ret

def get_by_name(name):
    sql = 'SELECT id FROM minor_factions WHERE name = ?'
    c = db.cursor()
    ret = c.execute(sql, (name,)).fetchone()
    if ret == None:
        return None
    else:
        return ret[0]

def get_systems(minor_faction_id):
    sql = 'SELECT edsm_id FROM system_minor_factions WHERE minor_faction_id = ?'
    ret = []
    c = db.cursor()
    rows = c.execute(sql, (minor_faction_id,)).fetchall()
    for row in rows:
        if row[0] != None:
            ret.append(row[0])
    return ret

