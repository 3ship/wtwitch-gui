#!/usr/bin/env python

import os
import sys
import re
import json
import subprocess
import time
import base64
from datetime import datetime
import encoded_images

def check_config():
    with open(wtwitch_config_file(), 'r') as config:
        config = json.load(config)
        player = config['player']
        quality = config['quality']
        colors = config['colors']
        print_offline_subs = config['printOfflineSubscriptions']
    return player, quality, colors, print_offline_subs

def adjust_config(setting, new_value):
    with open(wtwitch_config_file(), 'r') as config:
        config = json.load(config)
    config[setting] = new_value
    with open(wtwitch_config_file(), 'w') as nconfig:
        json.dump(config, nconfig)

def follow_streamer(s):
    new_entry = {'streamer': s}
    with open(wtwitch_config_file(), 'r') as config:
        config = json.load(config)
    if new_entry not in config['subscriptions']:
        config['subscriptions'].append(new_entry)
    with open(wtwitch_config_file(), 'w') as nconfig:
        json.dump(config, nconfig)

def unfollow_streamer(s):
    with open(wtwitch_config_file(), 'r') as config:
        config = json.load(config)
    new_subscriptions = []
    for i in config['subscriptions']:
        if i['streamer'] == s:
            continue
        else:
            new_subscriptions.append(i)
    config['subscriptions'] = new_subscriptions
    with open(wtwitch_config_file(), 'w') as nconfig:
        json.dump(config, nconfig)

def wtwitch_config_file():
    if 'APPDATA' in os.environ:
        confighome = os.environ['APPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:
        confighome = os.environ['XDG_CONFIG_HOME']
    else:
        confighome = os.path.join(os.environ['HOME'], '.config')
    configfile = os.path.join(confighome, 'wtwitch/config.json')
    return configfile

def wtwitch_subscription_cache():
    if 'LOCALAPPDATA' in os.environ:
        cachehome = os.environ['LOCALAPPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:
        cachehome = os.environ['XDG_CACHE_HOME']
    else:
        cachehome = os.path.join(os.environ['HOME'], '.cache')
    cachepath = os.path.join(cachehome, 'wtwitch/subscription-cache.json')
    return cachepath, cachehome

def extract_streamer_status():
    online_streamers = []
    online_package = []
    offline_streamers = []
    with open(wtwitch_subscription_cache()[0], 'r') as cache:
        cachefile = json.load(cache)
        for streamer in cachefile['data']:
            online_streamers.append(streamer['user_login'])
            login = streamer['user_login']
            name = streamer['user_name']
            categ = streamer['game_name']
            title = streamer['title']
            views = streamer['viewer_count']
            package = login,name,categ,title,views
            online_package.append(package)
    with open(wtwitch_config_file(), 'r') as config:
        configfile = json.load(config)
        subscriptions = configfile['subscriptions']
        for diction in subscriptions:
            streamer = diction['streamer']
            if streamer not in online_streamers:
                offline_streamers.append(streamer)
    online_package.sort()
    offline_streamers.sort()
    return online_package, offline_streamers

def last_seen(s):
    lastseen_dir = f'{wtwitch_subscription_cache()[1]}/wtwitch/lastSeen/{s}'
    try:
        with open(lastseen_dir) as lastseen:
            ts = int(lastseen.read())
            ts = datetime.utcfromtimestamp(ts)
            ts = ts.strftime('%Y-%m-%d - %H:%M')
            return ts
    except:
        return 'unknown'

def check_status():
    '''Call wtwitch c again when pressing the refresh button
    '''
    subprocess.run(['wtwitch', 'c'],
                    capture_output=True,
                    text=True
                    )

def fetch_vods(streamer):
    '''Run wtwitch v and extract all timestamps/titles of the streamer's VODs
    with regex. Cap the title length at 50 characters.
    '''
    # Make sure vods directory exists:
    if not os.path.isdir(f'{sys.path[0]}/vods'):
        os.makedirs(f'{sys.path[0]}/vods')
    # Make sure the streamer's vods file exist and set it's age:
    vods_file = f'{sys.path[0]}/vods/{streamer}.txt'
    if not os.path.isfile(vods_file):
        open(vods_file, 'a').close()
        cache_age = 10000
    else:
        cache_modified = os.path.getmtime(vods_file)
        cache_age = time.time() - cache_modified
    # Only update the vods file, if it's new or older than 1 hour:
    if cache_age > 3600:
        wtwitch_v = subprocess.check_output(['wtwitch', 'v', streamer],
                            text=True
                            )
        wtwitch_v = fr'{wtwitch_v}'
        with open(vods_file, 'w') as vods:
            vods.write(wtwitch_v)
    # Retrieve relevant data from vods file and return it:
    timestamps = []
    titles = []
    length = []
    timestamp_pattern = re.compile(r'\d{2}\S\d{2}.* \d{2}:\d{2}')
    titles_pattern = re.compile(r'(?<=\x1b\[0m\s)(.*?)(?=\s\x1b\[93m)')
    length_pattern = re.compile(r'\d+h\d+m')
    with open(vods_file, 'r') as vods:
        for line in vods:
            for match in timestamp_pattern.finditer(line):
                timestamps.append(match.group())
            for match in titles_pattern.finditer(line):
                titles.append(match.group())
            for match in length_pattern.finditer(line):
                length.append(match.group())
    return timestamps, titles, length

def start_vod(s, v):
    subprocess.run(['wtwitch', 'v', s, str(v)])

def start_stream(s):
    subprocess.run(['wtwitch', 'w', s])

def icon_paths():
    if not os.path.isdir(f'{sys.path[0]}/icons'):
        os.makedirs(f'{sys.path[0]}/icons')
    icon_dir_path = f'{sys.path[0]}/icons'

    icon_file_paths = {}
    for name in encoded_images.images:
        if not os.path.isfile(f'{icon_dir_path}/{name}.png'):
            with open(f'{icon_dir_path}/{name}.png', "wb") as icon_file:
                icon_data = base64.b64decode(encoded_images.images[name])
                icon_file.write(icon_data)
        icon_file_paths[name] = f'{icon_dir_path}/{name}.png'
    return icon_file_paths

def create_settings_file():
    default_settings = '{"show_info": "no", "show_info_preset": "online"}'
    if not os.path.isfile(f'{sys.path[0]}/settings.json'):
        with open(f'{sys.path[0]}/settings.json', 'w') as settings:
            settings.write(default_settings)

def change_settings_file(setting, new_value):
    with open(f'{sys.path[0]}/settings.json', 'r') as settings:
        settings = json.load(settings)
    settings[setting] = new_value
    with open(f'{sys.path[0]}/settings.json', 'w') as nsettings:
        json.dump(settings, nsettings)

def get_setting(k):
    with open(f'{sys.path[0]}/settings.json', 'r') as settings:
        settings = json.load(settings)
    return settings[k]