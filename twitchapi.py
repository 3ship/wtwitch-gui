#!/usr/bin/env python

import os
import re
import json
import subprocess

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
    return cachepath

def extract_streamer_status():
    online_streamers = []
    online_package = []
    offline_streamers = []
    with open(wtwitch_subscription_cache(), 'r') as cache:
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
    wtwitch_v = subprocess.run(['wtwitch', 'v', streamer],
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        text=True
                        )
    timestamps = re.findall(r'\[96m\[(\S* \d.*:\d.*):\d.*\]', wtwitch_v.stdout)
    titles = re.findall(r'\]\x1b\[0m\s*(\S.*)\s\x1b\[93m', wtwitch_v.stdout)
    length = re.findall(r'\x1b\[93m(\S*)\x1b\[0m', wtwitch_v.stdout)
    #for i in range(len(titles)):
    #    if len(titles[i]) > 50:
    #        titles[i] = titles[i][:50] + "..."
    return timestamps, titles, length