#!/usr/bin/env python

import os
import re
import json
import subprocess
from datetime import datetime

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
    online_streamers.sort()
    online_package.sort()
    offline_streamers.sort()
    return online_package, offline_streamers

def last_seen(s):
    lastseen_dir = f'{wtwitch_subscription_cache()[1]}/wtwitch/lastSeen/{s}'
    try:
        with open(lastseen_dir) as lastseen:
            for line in lastseen:
                ts = int(line)
                ts = datetime.utcfromtimestamp(ts)
                ts = ts.strftime('%Y-%m-%d - %H:%M')
                return ts
    except:
        return 'unknown'

def check_status():
    '''Call wtwitch c again when pressing the refresh button
    '''
    wtwitch_c = subprocess.run(['wtwitch', 'c'],
                        capture_output=True,
                        text=True
                        )

def fetch_vods(streamer):
    '''Run wtwitch v and extract all timestamps/titles of the streamer's VODs
    with regex. Cap the title length at 50 characters.
    '''
    wtwitch_v = subprocess.check_output(['wtwitch', 'v', streamer],
                        text=True
                        )
    wtwitch_v = fr'{wtwitch_v}'
    with open('vods.txt', 'w') as vods:
        vods.write(wtwitch_v)
    timestamps = []
    titles = []
    length = []
    timestamp_pattern = re.compile(r'\d{2}\S\d{2}.* \d{2}:\d{2}')
    titles_pattern = re.compile(r'(?<=\x1b\[0m\s)(.*?)(?=\s\x1b\[93m)')
    length_pattern = re.compile(r'\d+h\d+m')
    with open('vods.txt', 'r') as vods:
        for line in vods:
            for match in timestamp_pattern.finditer(line):
                timestamps.append(match.group())
            for match in titles_pattern.finditer(line):
                titles.append(match.group())
            for match in length_pattern.finditer(line):
                length.append(match.group())
    return timestamps, titles, length