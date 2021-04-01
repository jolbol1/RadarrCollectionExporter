#!/usr/bin/python3
import yaml
import sqlite3
import sys
import ast


def set_state(config, state):
    with open(config) as f:
        doc = yaml.safe_load(f)
    doc['collections'] = state
    with open(config, 'w') as f:
        yaml.safe_dump(doc, f, default_flow_style=False)

def radarrToPAC(config_path, radarrDBpath):
    print("Radarr to Plex Auto Collections is starting.")
    with open(config_path) as parameters:
        config = yaml.safe_load(parameters)

    PACconfig = config['collections']
    radarrDB = sqlite3.connect(radarrDBpath)

    collections = radarrDB.execute("SELECT Collection FROM Movies").fetchall()
    for row in collections:
        if row[0] != None:
            collect = str(row[0])
            dict = ast.literal_eval(collect)
            search_key = dict['name']
            collection = {str(dict['name']): {'tmdb_id': int(dict['tmdbId']), 'add_to_radarr' : bool(True)}}
            PACconfig.update(collection)
            set_state(configPath, PACconfig)



radarrToPAC(sys.argv[1], sys.argv[2])
