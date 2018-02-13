#!/usr/bin/python

import settings
import sqlite3
import pprint

db = sqlite3.connect(settings.db_path)
pp = pprint.PrettyPrinter(indent=2)

def get(id):
    sql = 'SELECT * FROM systems WHERE edsm_id = ?;'
    c = db.cursor()
    ret = c.execute(sql, (id,)).fetchone()
    return ret

def get_by_name(name):
    sql = 'SELECT edsm_id FROM systems WHERE name = ?'
    c = db.cursor()
    ret = c.execute(sql, (name,)).fetchone()
    if ret == None:
        return None
    else:
        return ret[0]

def get_factions(edsm_id):
    sql = 'SELECT * FROM system_minor_factions WHERE edsm_id = ? ORDER BY influence DESC'
    ret = []
    c = db.cursor()
    rows = c.execute(sql, (edsm_id,)).fetchall()
    for row in rows:
        ret.append(row)
    return ret

