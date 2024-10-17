import os
import sys
import json

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

create_settings_file()