#!/usr/bin/python3
import sqlite3
import sys
import ast
import datetime
import argparse
import logging as log
import util
import ruamel.yaml

parser = argparse.ArgumentParser()
parser.add_argument(dest="config_path",
                    help="Run with desired config.yml file",
                    type=str)
parser.add_argument(dest="db_path",
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
                    help="Can be 'true' or 'false'. Overwrites the config setting for all collections added here. Refer to PAC wiki for more details",
                    type=str)
parser.add_argument("-is", "--ignore-singles", "--ignore_single",
                    dest="ignore_single",
                    choices=['false', 'true'],
                    help="Can be 'true' or 'false'. This will not add collections to the config where radarr only has 1 movie in the collection",
                    type=str)
parser.add_argument("-v", "--verbose",
                    action = "store_true",
                    dest="verbose",
                    help="More detailed logs.")
parser.add_argument("-o", "--overwrite",
                    action = "store_true",
                    dest="overwrite",
                    help="Overwrite collection with mathing name")
parser.add_argument("-pmm", "--plexmetamanager",
                    action = "store_true",
                    dest="pmm",
                    help="Overwrite collection with mathing name")


args = parser.parse_args()

if args.verbose:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    log.info("Verbose output.")
else:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)


def cleanNullTerms(original):
    filtered = {k: v for k, v in original.items() if v is not None}
    original.clear()
    original.update(filtered)
    return original

def firstRun(config_path):
    try:
        with open(config_path, "r") as conf:
        # Load the yaml config
            return False if 'RadarrToPMM' in conf.read() else True
            #Close it now we have it saved as a var
            conf.close() 
    # Grab the collections from the config
    except:
        log.info("Could not open the specified config at {} are you sure the path is correct".format(config_path))
        return False

def radarrToPAC(config_path, radarrDBpath, **kwargs):
    #Start yaml
    yaml = ruamel.yaml.YAML()
    #Log the start
    log.info("{} Radarr to Plex Auto Collections is starting.".format(datetime.datetime.now()))
    #try to open the config
    try:
        with open(config_path, "r") as conf:
        # Load the yaml config
            loaded_config = ruamel.yaml.load(conf, ruamel.yaml.RoundTripLoader) 
            #Close it now we have it saved as a var
            conf.close() 
        # Grab the collections from the config
    except:
        log.info("Could not open the specified config at {} are you sure the path is correct".format(config_path))
        exit()
    # Grab collections
    PACconfig = loaded_config['collections']
    # Check in case they have no existing set up
    if PACconfig is None:
        PACconfig = {}
    #Open the radarr database. Attempt to grab movies. Except if it fails.
    radarrDB = sqlite3.connect(radarrDBpath)
    try:
        if kwargs['ignore_single'] == 'true':
            collections = radarrDB.execute("SELECT Collection, COUNT(*) FROM Movies GROUP BY Collection HAVING COUNT(*) > 1").fetchall()
        else:
            collections = radarrDB.execute("SELECT distinct Collection FROM Movies").fetchall()                 
    except:
        log.info("Unable to find movies in the radarr database. Are you sure the path is correct!")
        exit()
    # Variables for logging
    ignored = 0
    added = 0
    # Sort through the radarr movie collections
    first_run = firstRun(config_path)
    for row in collections:
        # Make sure theres actually collections in the database
        if row[0] is None:
            continue
        # Grab the collection enry     
        collect = str(row[0])
        dict = ast.literal_eval(collect)
        search_key = dict['name']
        # Test if it exists in the config already and see how to handle an overwrite
        if search_key in PACconfig and not args.overwrite:
            log.debug("Ignored {} as it is already in the config".format(search_key))
            ignored += 1
        else:
            # Set up the collection entry.
            variables = {'tmdb_collection': int(dict['tmdbId']), 'collection_mode' : kwargs['collection_mode'], 'add_to_arr' : bool(kwargs['add_radarr']), 'sync_mode' : kwargs['sync_mode']}
            variables_clean = cleanNullTerms(variables)
            # Add comment to start of radarrToPMM entries
            if added is 0 and first_run:
                PACconfig.yaml_set_comment_before_after_key(search_key, before="\n ############################# \n # Added by RadarrToPMM \n Please leve this and alll the collections below at end  \n ############################# \n")                
            # Set entry into the config
            PACconfig[search_key] = variables_clean             
            added += 1
            log.debug("Added {} to plex-auto-collections".format(search_key))
    # Write new config to file.
    with open(config_path, 'w') as conf:
        ruamel.yaml.dump(loaded_config, conf, ruamel.yaml.RoundTripDumper)   
    log.info("{} Radarr to Plex Auto Collections finished. Added: {}, Ignored: {}".format(datetime.datetime.now(), added, ignored))

radarrToPAC(args.config_path, args.db_path, sync_mode=args.sync_mode, collection_mode=args.collection_mode, add_radarr=args.add_radarr, ignore_single=args.ignore_single)
