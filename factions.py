#!/usr/bin/python

import settings
import urllib
import os.path
import sqlite3
import time
import json_lines

db = sqlite3.connect(settings.db_path)

def init():
    # Do we have to stand up a fresh database?
    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='minor_factions';"
    result = db.execute(sql).fetchone()
    if result == None:
        print "Prep DB"
        prep_database();

    # Table status
    tables = ['minor_factions', 'systems', 'system_minor_factions']
    for table in tables:
        sql = "SELECT COUNT(*) FROM %s;" % (table)
        count = db.execute(sql).fetchone()[0]
        print "%s %s." % (table, count)


def download_data_source(url, target_file):
    # Initial factions source file.
    download_source = False
    # Do we have the data file?
    if os.path.exists(target_file):
        if time.time() - os.path.getmtime(target_file) > (1 * 24 * 60 * 60):
            os.remove(target_file)
            download_source = True
    else:
        download_source = True

    # Download the source file if needed.
    if download_source:
        print 'Downloading JSONL file to %s.' % (target_file)
        urllib.urlretrieve(url, target_file)


def prep_database():
    prep_tables()

    download_data_source("https://eddb.io/archive/v5/systems_populated.jsonl", settings.systems_jsonl)
    download_data_source("https://eddb.io/archive/v5/factions.jsonl", settings.factions_jsonl)
    init_factions(settings.monitored_factions)
    init_systems()
    init_faction_neighbours();


def prep_tables():
    # Standup the tables.
    tables = [
        'CREATE TABLE IF NOT EXISTS systems(edsm_id INT PRIMARY KEY, name TEXT, government TEXT, x REAL, y REAL, z REAL, population INT, security, primary_economy, updated_at, controlling_minor_faction_id)',
        'CREATE INDEX IF NOT EXISTS system_name ON systems(name);',
        'CREATE TABLE IF NOT EXISTS minor_factions(id INT PRIMARY KEY, name TEXT, updated_at, government TEXT, state TEXT, is_player_faction INT)',
        'CREATE INDEX IF NOT EXISTS minor_faction_name ON minor_factions(name);',
        'CREATE TABLE IF NOT EXISTS system_minor_factions(edsm_id INT, minor_faction_id INT, influence REAL, state TEXT, PRIMARY KEY(edsm_id, minor_faction_id))',
            ]
    for sql in tables:
        print sql
        db.execute(sql)
    db.commit()


"""
 " Load out factions into the database.
"""
def init_factions(factions):
    print "Searching factions..."
    with json_lines.open(settings.factions_jsonl) as reader:
        for item in reader:
            for faction in factions:
                if isinstance(faction, int):
                    if item['id'] == faction:
                        save_faction(item)
                else:
                    if item['name'] == faction:
                        save_faction(item)


def init_systems():
    print "Searching systems..."
    faction_ids = []
    sql = 'SELECT id FROM minor_factions WHERE name IN %s' % (in_clause(settings.monitored_factions))
    c = db.cursor()
    c.execute(sql)
    for row in c:
        faction_ids.append(row[0])
    print faction_ids
    with json_lines.open(settings.systems_jsonl) as reader:
        for item in reader:
            print item['name'],"                \r",
            for faction in item['minor_faction_presences']:
                if faction['minor_faction_id'] in faction_ids:
                    save_system(item)
                    print ""


def init_faction_neighbours():
    c = db.cursor()
    c.execute('SELECT minor_faction_id FROM system_minor_factions;')
    faction_ids = []
    for row in c:
        faction_ids.append(row[0])
    # Initilise these factions.
    init_factions(faction_ids)


def save_faction(item):
    sql = "INSERT OR REPLACE INTO minor_factions VALUES (?, ?, ?, ?, ?, ?);"
    data = [
            item['id'],
            item['name'],
            item['updated_at'],
            item['government'],
            item['state'],
            item['is_player_faction'],
            ]
    db.execute(sql, data)
    db.commit()


def save_system(item):
    sql = "INSERT OR REPLACE INTO systems VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
    faction_sql = "INSERT OR REPLACE INTO system_minor_factions VALUES (?, ?, ?, ?);"
    data = [
            item['edsm_id'],
            item['name'],
            item['government'],
            item['x'],
            item['y'],
            item['z'],
            item['population'],
            item['security'],
            item['primary_economy'],
            item['updated_at'],
            item['controlling_minor_faction_id'],
            ]
    db.execute(sql, data)
    for faction in item['minor_faction_presences']:
        data = [
                item['edsm_id'],
                faction['minor_faction_id'],
                faction['influence'],
                faction['state'],
                ]
        db.execute(faction_sql, data)


"""
 " Helper function to return a line count of a file.
"""
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f, 1):
            pass
    return i


"""
 " Helper function to return a string suitable for an IN clause in SQL.
"""
def in_clause(inClause):
    ret = "('" + "','".join(inClause) + "')"
    return ret

init()
