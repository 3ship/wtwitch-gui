import tkinter as tk
from tkinter import ttk
import conf


def get_icons():
    '''Imports and assigns the icons to a dictionary. Sets the app icon for the window.'''
    # Import icons
    icon_files = conf.icon_paths()
    theme = conf.get_setting('theme')
    ending = properties.get(theme, {}).get('icon_ending', '')
    
    icon_names = [
        'unfollow_icon', 'vod_icon', 'play_icon', 'close_icon', 'settings_icon',
        'link_icon', 'expand_icon', 'collapse_icon', 'follow_icon',
        'play_stream_icon', 'refresh_icon'
    ]
    
    icons = {name: tk.PhotoImage(file=icon_files[f'{name}{ending}']) for name in icon_names}
    
    # Special cases without theme suffix
    icons['streaming_icon'] = tk.PhotoImage(file=icon_files['streaming_icon'])
    icons['offline_icon'] = tk.PhotoImage(file=icon_files['offline_icon'])
    icons['app_icon'] = tk.PhotoImage(file=icon_files['app_icon'])
    
    return icons


def default_radiobutton(master, *args, **kwargs):
    radio_theme = theme['radiobutton']
    widget_kwargs = {
        'bg': theme['bg'],
        'fg': theme['fg'],
        'activeforeground': theme['fg'],
        'activebackground': theme['activebackground'],
        'selectcolor': radio_theme['selectcolor'],
        'disabledforeground': theme['fg'],
        'anchor': 'w',
        **base_widget_attributes,
        **kwargs
    }
    return tk.Radiobutton(master, **widget_kwargs)


def default_separator(master, start_row=0, span=5, **kwargs):
    sep1_kwargs = {
        'bg': theme['separator_bg1'],
        'height': 1,
        'borderwidth': 1,
        'relief': "flat",
        **kwargs
    }
    sep2_kwargs = {
        'bg': theme['separator_bg2'],
        'height': 1,
        'borderwidth': 1,
        'relief': "flat",
        **kwargs
    }

    sep1 = tk.Frame(master, **sep1_kwargs)
    sep2 = tk.Frame(master, **sep2_kwargs)

    sep1.grid(row=start_row, column=0, sticky='ew', columnspan=span)
    sep2.grid(row=start_row + 1, column=0, sticky='ew', columnspan=span)

    return sep1, sep2


def default_canvas(master, **kwargs):
    widget_kwargs = {
        'bg': theme['bg'],
        **base_widget_attributes,
        **kwargs
    }
    return tk.Canvas(master, **widget_kwargs)


def default_frame(master, **kwargs):
    widget_kwargs = {
        'bg': theme['bg'],
        **base_widget_attributes,
        **kwargs
    }
    return tk.Frame(master, **widget_kwargs)


def default_label(master, *args, **kwargs):
    fg_color = theme['offline_fg'] if 'offline' in args else theme['fg']
    widget_kwargs = {
        'bg': theme['bg'],
        'fg': fg_color,
        **base_widget_attributes,
        **kwargs
    }
    return tk.Label(master, **widget_kwargs)


def default_button(master, *args, **kwargs):
    fg_color = theme['offline_fg'] if 'offline' in args else theme['fg']
    widget_kwargs = {
        'bg': theme['bg'],
        'fg': fg_color,
        'activebackground': theme['activebackground'],
        'activeforeground': theme['fg'],
        'disabledforeground': fg_color,
        **base_widget_attributes,
        **kwargs
    }
    return tk.Button(master, **widget_kwargs)


def default_entry(master, *args, **kwargs):
    entry_theme = theme['entry']
    widget_kwargs = {
        'bg': entry_theme['bg'],
        'fg': entry_theme['fg'],
        'insertbackground': entry_theme['cursor_color'],
        **base_widget_attributes,
        **kwargs
    }
    
    entry = tk.Entry(master, **widget_kwargs)
    
    # Define context menu functions inside the default_entry function
    def on_cut():
        entry.event_generate("<<Cut>>")

    def on_copy():
        entry.event_generate("<<Copy>>")

    def on_paste():
        entry.event_generate("<<Paste>>")

    def show_context_menu(event):
        context_menu.tk_popup(event.x_root, event.y_root)

    # Create a context menu and apply the theme
    context_menu = tk.Menu(master, tearoff=0,
                            bg=theme['bg'],
                            fg=theme['fg'],
                            activebackground=theme['activebackground'],
                            activeforeground=theme['fg'],
                            relief='flat'
                            )
    context_menu.add_command(label="Cut", command=on_cut)
    context_menu.add_command(label="Copy", command=on_copy)
    context_menu.add_command(label="Paste", command=on_paste)
    
    # Bind right-click to show context menu
    entry.bind("<Button-3>", show_context_menu)
    
    return entry


def scrollbar_presets(master):
    scrollbar_theme = theme['scrollbar']
    scrollbar_width = 16
    style = ttk.Style(master)
    style.configure('Vertical.TScrollbar',
                    gripcount=0,
                    relief='flat',
                    troughrelief='flat',
                    width=scrollbar_width,
                    groovewidth=scrollbar_width,
                    arrowsize=scrollbar_width,
                    background=scrollbar_theme['bg'],
                    troughcolor=scrollbar_theme['trough'],
                    arrowcolor=scrollbar_theme['arrow']
                    )
    # Mouse hover:
    style.map("Vertical.TScrollbar",
                    background=[("active", scrollbar_theme['active'])]
                    )


# Base attributes for all color themes:
base_widget_attributes = {
    'highlightthickness': 0,
    'relief': 'flat',
    'border': 0
}


# Add and edit color schemes here.
# The name pattern 'lower_case' will be edited to 'Lower Case' in the settings
# Available icon endings: '_light', '_yellow', '' (empty, for black theme)
properties = {
    'gnome_dark': {
        'bg': '#333333',
        'fg': '#BDBDBD',
        'offline_fg': '#A4A4A4',
        'activebackground': '#3F3F3F',
        'selectcolor': '#242424',
        'separator_bg1': '#252525',
        'separator_bg2': '#484848',
        'entry': {
            'bg': '#444444',
            'fg': '#BDBDBD',
            'cursor_color': '#FFFFFF',
        },
        'scrollbar': {
            'bg': '#2c2c2c',
            'trough': '#363636',
            'arrow': '#BDBDBD',
            'active': '#222222'
        },
        'radiobutton': {
            'selectcolor': '#333333'
        },
        'icon_ending': '_light'
    },
    'gnome_light': {
        'bg': '#FAFAFA',
        'fg': '#101010',
        'offline_fg': '#333333',
        'activebackground': '#EFEFEF',
        'selectcolor': '#FAFAFA',
        'separator_bg1': '#E3E3E3',
        'separator_bg2': '#FFFFFF',
        'entry': {
            'bg': '#E1E1E1',
            'fg': '#101010',
            'cursor_color': '#000000',
        },
        'scrollbar': {
            'bg': '#EFEFEF',
            'trough': '#DBDBDB',
            'arrow': '#2c2c2c',
            'active': '#FFFFFF'
        },
        'radiobutton': {
            'selectcolor': '#FAFAFA'
        },
        'icon_ending': ''
    },
    'breeze_dark': {
        'bg': '#232629',
        'fg': '#eff0f1',
        'offline_fg': '#939393',
        'activebackground': '#31363b',
        'selectcolor': '#2c2c2c',
        'separator_bg1': '#17191B',
        'separator_bg2': '#3a3a3a',
        'entry': {
            'bg': '#31363b',
            'fg': '#eff0f1',
            'cursor_color': '#ffffff',
        },
        'scrollbar': {
            'bg': '#232629',
            'trough': '#31363b',
            'arrow': '#eff0f1',
            'active': '#3a3a3a'
        },
        'radiobutton': {
            'selectcolor': '#232629'
        },
        'icon_ending': '_light'
    },
    'breeze_light': {
        'bg': '#eff0f1',
        'fg': '#31363b',
        'offline_fg': '#5f6368',
        'activebackground': '#e5e5e5',
        'selectcolor': '#eff0f1',
        'separator_bg1': '#d5d5d5',
        'separator_bg2': '#ffffff',
        'entry': {
            'bg': '#ffffff',
            'fg': '#31363b',
            'cursor_color': '#000000',
        },
        'scrollbar': {
            'bg': '#f5f5f5',
            'trough': '#e5e5e5',
            'arrow': '#232629',
            'active': '#ffffff'
        },
        'radiobutton': {
            'selectcolor': '#eff0f1'
        },
        'icon_ending': ''
    },
    'dusky_blue': {
        'bg': '#30343F',
        'fg': '#E3E3BD',
        'offline_fg': '#B0B07D',
        'activebackground': '#39404F',
        'selectcolor': '#24292F',
        'separator_bg1': '#262A34',
        'separator_bg2': '#4B515F',
        'entry': {
            'bg': '#414550',
            'fg': '#E3E3BD',
            'cursor_color': '#E3E3BD',
        },
        'scrollbar': {
            'bg': '#2F3441',
            'trough': '#3A3F4C',
            'arrow': '#D27F7F',
            'active': '#5A6E73'
        },
        'radiobutton': {
            'selectcolor': '#30343F'
        },
        'icon_ending': '_yellow'
    },
    'rusty_red': {
        'bg': '#402D2D',
        'fg': '#BDBDBD',
        'offline_fg': '#A4A4A4',
        'activebackground': '#4B3535',
        'selectcolor': '#7D2A2A',
        'separator_bg1': '#362525',
        'separator_bg2': '#5A3F3F',
        'entry': {
            'bg': '#4A3636',
            'fg': '#BDBDBD',
            'cursor_color': '#FFFFFF',
        },
        'scrollbar': {
            'bg': '#3A2C2C',
            'trough': '#4A2C2C',
            'arrow': '#D15656',
            'active': '#8A3F3F'
        },
        'radiobutton': {
            'selectcolor': '#402D2D'
        },
        'icon_ending': '_light'
    },
    'light_blues': {
        'bg': '#EAF5FB',
        'fg': '#0D1B2A',
        'offline_fg': '#2B3B52',
        'activebackground': '#D9E8EF',
        'selectcolor': '#C1D3DA',
        'separator_bg1': '#C4DDE9',
        'separator_bg2': '#E3F4FA',
        'entry': {
            'bg': '#DAEDF3',
            'fg': '#0D1B2A',
            'cursor_color': '#0D1B2A',
        },
        'scrollbar': {
            'bg': '#D4E8F1',
            'trough': '#BED5DC',
            'arrow': '#8A9BAA',
            'active': '#487A8B'
        },
        'radiobutton': {
            'selectcolor': '#EAF5FB'
        },
        'icon_ending': ''
    },
    'light_reds': {
        'bg': '#FFF5F5',
        'fg': '#202020',
        'offline_fg': '#3B2B2B',
        'activebackground': '#FFE0E0',
        'selectcolor': '#FFBBBB',
        'separator_bg1': '#FFDADA',
        'separator_bg2': '#FFF0F0',
        'entry': {
            'bg': '#FFE8E8',
            'fg': '#202020',
            'cursor_color': '#202020',
        },
        'scrollbar': {
            'bg': '#FFD5D5',
            'trough': '#FFC0C0',
            'arrow': '#BF3030',
            'active': '#E57373'
        },
        'radiobutton': {
            'selectcolor': '#FFF5F5'
        },
        'icon_ending': ''
    },
    'twitchy': {
        'bg': '#2D1B3C',
        'fg': '#E6E6FA',
        'offline_fg': '#A299C0',
        'activebackground': '#3C2B4D',
        'selectcolor': '#541673',
        'separator_bg1': '#35233B',
        'separator_bg2': '#4A2F5A',
        'entry': {
            'bg': '#412753',
            'fg': '#E6E6FA',
            'cursor_color': '#F0E6FF',
        },
        'scrollbar': {
            'bg': '#3A2945',
            'trough': '#50375A',
            'arrow': '#D1ACFF',
            'active': '#622A8F'
        },
        'radiobutton': {
            'selectcolor': '#2D1B3C'
        },
        'icon_ending': '_light'
    },
    'neon_city': {
        'bg': '#1A1A2E',
        'fg': '#0DF9FF',
        'offline_fg': '#0BBABF',
        'activebackground': '#16213E',
        'selectcolor': '#08D9D6',
        'separator_bg1': '#141425',
        'separator_bg2': '#2B2B48',
        'entry': {
            'bg': '#0E153A',
            'fg': '#0DF9FF',
            'cursor_color': '#00FFFF',
        },
        'scrollbar': {
            'bg': '#212F45',
            'trough': '#1A1A2E',
            'arrow': '#00FFFF',
            'active': '#1282A2'
        },
        'radiobutton': {
            'selectcolor': '#3A214F'
        },
        'icon_ending': '_magenta'
    },
    'midnight': {
        'bg': '#121212',
        'fg': '#bbbbbb',
        'offline_fg': '#555555',
        'activebackground': '#1d1d1d',
        'selectcolor': '#555555',
        'separator_bg1': '#252525',
        'separator_bg2': '#353535',
        'entry': {
            'bg': '#1A1A1A',
            'fg': '#bbbbbb',
            'cursor_color': '#FFFFFF',
        },
        'scrollbar': {
            'bg': '#555555',
            'trough': '#1d1d1d',
            'arrow': '#252525',
            'active': '#353535'
        },
        'radiobutton': {
            'selectcolor': '#121212'
        },
        'icon_ending': '_light'
    }
}


# Fonts:
font_10 = ('', 10)
font_12 = ('Cantarell', 12)
font_12_b = ('Cantarell', 12, 'bold')
font_13_b = ('Cantarell', 13, 'bold')
# Retrieves the user setting:
current_theme = conf.get_setting('theme')
# Retrieves colors from dictionary:
theme = properties[current_theme]