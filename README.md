# RadarrToPAC
Gets all the collections from Radarr and adds them to Plex Auto Collections

To use:
`python3 radarrToPAC.py -c /path/to/plex-auto-collections/config.yml -db /path/to/radarr/radarr.db`

The above also has 3 optional arguments
```
  -sync {append,sync}, --sync {append,sync}, --sync-mode {append,sync}
                        Sync mode, can be 'append' or 'sync'. Refer to PAC
                        wiki for more details
  -cm {hide,default,hide_items,show_items}, --collection-mode {hide,default,hide_items,show_items}, --collection_mode {hide,default,hide_items,show_items}
                        4 modes, can be 'hide','default', 'hide_items' or
                        'show_items. Refer to PAC wiki for more details
  -add {false,true}, --add-to-radarr {false,true}, --add-radarr {false,true}
                        Can be 'true' or 'false', 'hide_items'. Overwrites the
                        config setting for all collections added here. Refer
                        to PAC wiki for more details
```

If for example you use all the options, the added collections will look like:
```
  Bond Collection:
    add_to_radarr: true
    collection_mode: default
    sync_mode: sync
    tmdb_id: 56566
```