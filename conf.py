#!/usr/bin/env python

import os
import sys
import re
import json
import subprocess
import time
import locale
import base64
from datetime import datetime

def wtwitch_config_file():
    if 'APPDATA' in os.environ:
        confighome = os.environ['APPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:
        confighome = os.environ['XDG_CONFIG_HOME']
    else:
        confighome = os.path.join(os.environ['HOME'], '.config')
    return os.path.join(confighome, 'wtwitch/config.json')

def wtwitch_subscription_cache():
    if 'LOCALAPPDATA' in os.environ:
        cachehome = os.environ['LOCALAPPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:
        cachehome = os.environ['XDG_CACHE_HOME']
    else:
        cachehome = os.path.join(os.environ['HOME'], '.cache')
    cachepath = os.path.join(cachehome, 'wtwitch/subscription-cache.json')
    onlinesubs_path = os.path.join(cachehome, 'wtwitch/online-subs')
    if not os.path.isfile(cachepath):
        default_cache = {"data": [], "pagination": {}}
        with open(cachepath, 'w') as initcachepath:
            json.dump(default_cache, initcachepath, indent=4)
    if not os.path.isfile(onlinesubs_path):
        open(onlinesubs_path, 'a')
    return cachepath, onlinesubs_path, cachehome

def read_config():
    with open(wtwitch_config_file(), 'r') as config:
        return json.load(config)

def write_config(config):
    with open(wtwitch_config_file(), 'w') as nconfig:
        json.dump(config, nconfig, indent=4)

def check_config():
    config = read_config()
    player = config.get('player')
    quality = config.get('quality')
    colors = config.get('colors')
    print_offline_subs = config.get('printOfflineSubscriptions')
    return player, quality, colors, print_offline_subs

def adjust_config(setting, new_value):
    config = read_config()
    config[setting] = new_value
    write_config(config)

def follow_streamer(s):
    new_entry = {'streamer': s.lower()}
    config = read_config()
    if new_entry not in config['subscriptions']:
        config['subscriptions'].append(new_entry)
        write_config(config)

        # Check if the streamer is in the subscription cache and add to the
        # online-subs file if present
        cachepath, onlinesubs_path, _ = wtwitch_subscription_cache()
        with open(cachepath, 'r') as cache:
            cachefile = json.load(cache)
            for streamer in cachefile['data']:
                if streamer['user_login'] == s:
                    with open(onlinesubs_path, 'a') as f:
                        f.write(f"\n{s}")
                    break

def unfollow_streamer(s):
    config = read_config()
    config['subscriptions'] = [i for i in config['subscriptions'] if i['streamer'] != s]
    write_config(config)
    
    # Remove the streamer from the online-subs file
    _, onlinesubs_path, _ = wtwitch_subscription_cache()
    with open(onlinesubs_path, 'r') as f:
        online_lines = f.read().splitlines()
    online_lines = [line for line in online_lines if line != s]
    with open(onlinesubs_path, 'w') as f:
        f.write('\n'.join(online_lines))

def extract_streamer_status():
    cachepath, onlinesubs_path, _ = wtwitch_subscription_cache()
    online_streamers = []
    online_package = []
    offline_streamers = []

    # Read the online-subs file
    with open(onlinesubs_path, 'r') as f:
        online_lines = f.read().splitlines()
    
    # Read the cache file
    with open(cachepath, 'r') as cache:
        cachefile = json.load(cache)
        for streamer in cachefile['data']:
            if streamer['user_login'] in online_lines:
                online_streamers.append(streamer['user_login'])
                login = streamer['user_login']
                name = streamer['user_name']
                categ = streamer['game_name']
                title = streamer['title']
                views = streamer['viewer_count']
                package = login, name, categ, title, views
                online_package.append(package)

    # Read the config file
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
    _, _, cachehome = wtwitch_subscription_cache()
    lastseen_dir = f'{cachehome}/wtwitch/lastSeen/{s}'
    try:
        with open(lastseen_dir) as lastseen:
            ts = int(lastseen.read())
            ts = datetime.utcfromtimestamp(ts)
            ts = ts.strftime('%Y-%m-%d - %H:%M')
            return ts
    except Exception:
        return 'unknown'


def ensure_vod_directory_and_file(vods_path: str, vods_file: str) -> float:
    if not os.path.isdir(vods_path):
        os.makedirs(vods_path)
    if not os.path.isfile(vods_file):
        open(vods_file, 'a').close()
        return 10000.0
    else:
        cache_modified = os.path.getmtime(vods_file)
        return time.time() - cache_modified


def fetch_vods(streamer: str) -> tuple[list[str], list[str], list[str]]:
    """
    Run wtwitch v and extract all timestamps/titles of the streamer's VODs with regex.
    """
    # Set the locale to ensure date and time formats are handled correctly
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    vods_path = f'{sys.path[0]}/vods'
    vods_file = f'{vods_path}/{streamer}.txt'

    cache_age = ensure_vod_directory_and_file(vods_path, vods_file)
    if cache_age > 3600:
        wtwitch_v = subprocess.check_output(['wtwitch', 'v', streamer])
        with open(vods_file, 'wb') as vods:
            vods.write(wtwitch_v)

    timestamps, dates, times, titles, lengths = [], [], [], [], []

    # Adjusted regex patterns
    date_pattern = re.compile(r'\d{2}[./-]\d{2}[./-]\d{2}')
    time_pattern = re.compile(r'\d{2}:\d{2}:\d{2}')
    titles_pattern = re.compile(r'\d+\.\s\x1b\[96m\[.*?\]\x1b\[0m\s(.*?)\s\x1b\[93m')
    length_pattern = re.compile(r'\x1b\[93m\((.*?)\)\x1b\[0m')

    with open(vods_file, 'rb') as vods:
        content = vods.read().decode('utf-8')  # Decode bytes to string
        
        dates = date_pattern.findall(content)
        times = time_pattern.findall(content)
        titles = titles_pattern.findall(content)
        lengths = [f"({match})" for match in length_pattern.findall(content)]

        timestamps = [f"{date} - {time}" for date, time in zip(dates, times)]

    return timestamps, titles, lengths


def check_status():
    '''Call wtwitch c again when pressing the refresh button
    '''
    subprocess.run(['wtwitch', 'c'],
                    capture_output=True,
                    text=True
                    )

def start_vod(s, v):
    subprocess.run(['wtwitch', 'v', s, str(v)])

def start_stream(s):
    subprocess.run(['wtwitch', 'w', s])


def icon_paths():
    icon_dir_path = f'{sys.path[0]}/icons'
    
    # Gather all PNG files in the directory
    icon_file_paths = {
        os.path.splitext(name)[0]: f'{icon_dir_path}/{name}'
        for name in os.listdir(icon_dir_path)
        if name.endswith('.png')
    }
    
    return icon_file_paths


def create_settings_file():
    default_settings = {
        "show_info": "no",
        "show_info_preset": "online",
        "theme": "gnome_light",
        "extra_buttons": "yes",
        "window_size": "285x450"
    }
    settings_path = f'{sys.path[0]}/settings.json'
    
    if not os.path.isfile(settings_path):
        with open(settings_path, 'w') as settings:
            json.dump(default_settings, settings, indent=4)
    else:
        with open(settings_path, 'r') as settings:
            current_settings = json.load(settings)
        
        # Update missing keys with default values
        for key, value in default_settings.items():
            if key not in current_settings:
                current_settings[key] = value
        
        with open(settings_path, 'w') as settings:
            json.dump(current_settings, settings, indent=4)


def change_settings_file(setting, new_value):
    settings_path = f'{sys.path[0]}/settings.json'
    with open(settings_path, 'r') as settings:
        current_settings = json.load(settings)
    
    # Check if the setting exists
    if setting in current_settings:
        current_settings[setting] = new_value
    else:
        raise KeyError(f"The setting '{setting}' does not exist in the settings file.")
    
    with open(settings_path, 'w') as settings:
        json.dump(current_settings, settings, indent=4)


def get_setting(k):
    settings_path = f'{sys.path[0]}/settings.json'
    with open(settings_path, 'r') as settings:
        current_settings = json.load(settings)
    
    # Check if the setting exists
    if k in current_settings:
        return current_settings[k]
    else:
        raise KeyError(f"The setting '{k}' does not exist in the settings file.")


def is_gnome():
    return os.environ.get('XDG_CURRENT_DESKTOP') == 'GNOME'