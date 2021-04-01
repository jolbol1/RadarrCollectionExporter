#!/usr/bin/python3
import yaml
import sqlite3
import sys
import ast
import datetime
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config-path", "--config_path",
                    dest="config_path",
                    help="Run with desired config.yml file",
                    type=str)
parser.add_argument("-db", "--db-path", "--database-path",
                    dest="db_path",
                    help="The radarr database path",
                    type=str)
parser.add_argument("-sync", "--sync", "--sync-mode",
                    dest="sync_mode",
                    choices=['append', 'sync'],
                    help="Sync mode, can be 'append' or 'sync'. Refer to PAC wiki for more details",
                    type=str)
parser.add_argument("-cm", "--collection-mode", "--collection_mode",
                    dest="collection_mode",
                    choices=['hide', 'default', 'hide_items', 'show_items'],
                    help="4 modes, can be 'hide','default', 'hide_items' or 'show_items. Refer to PAC wiki for more details",
                    type=str)
parser.add_argument("-add", "--add-to-radarr", "--add-radarr",
                    dest="add_radarr",
                    choices=['false', 'true'],
                    help="Can be 'true' or 'false', 'hide_items'. Overwrites the config setting for all collections added here. Refer to PAC wiki for more details",
                    type=str)


args = parser.parse_args()

def set_state(config, state):
    with open(config) as f:
        doc = yaml.safe_load(f)
    doc['collections'] = state
    with open(config, 'w') as f:
        yaml.safe_dump(doc, f, default_flow_style=False)

def cleanNullTerms(original):
    filtered = {k: v for k, v in original.items() if v is not None}
    original.clear()
    original.update(filtered)
    return original



def radarrToPAC(config_path, radarrDBpath, **kwargs):
    print(kwargs['collection_mode'])
    print("{} Radarr to Plex Auto Collections is starting.".format(datetime.datetime.now()))
    with open(config_path) as parameters:
        config = yaml.safe_load(parameters)

    PACconfig = config['collections']
    radarrDB = sqlite3.connect(radarrDBpath)

    collections = radarrDB.execute("SELECT distinct Collection FROM Movies").fetchall()
    ignored = 0
    added = 0
    for row in collections:
        if row[0] != None:
            collect = str(row[0])
            dict = ast.literal_eval(collect)
            search_key = dict['name']
            if dict['name'] in PACconfig:
                print("Ignored {} as it is already in the config".format(dict['name']))
                ignored += 1
            else:
                variables = {'tmdb_id': int(dict['tmdbId']), 'add_to_radarr' : bool(True), 'collection_mode' : kwargs['collection_mode'], 'add_to_radarr' : kwargs['add_radarr'], 'sync_mode' : kwargs['sync_mode']}
                variables_clean = cleanNullTerms(variables)
                collection_raw = {str(dict['name']): variables_clean}
                collection = cleanNullTerms(collection_raw)
                PACconfig.update(collection)
                set_state(config_path, PACconfig)
                added += 1
                print("Added {} to plex-auto-collections".format(dict['name']))

    print("{} Radarr to Plex Auto Collections finished. Added: {}, Ignored: {}".format(datetime.datetime.now(), added, ignored))

radarrToPAC(args.config_path, args.db_path, sync_mode=args.sync_mode, collection_mode=args.collection_mode, add_radarr=args.add_radarr)
