import tkinter as tk
from tkinter import ttk
import settings


def default_radiobutton(master, *args, **kwargs):
    return tk.Radiobutton(
        master,
        bg=theme['bg'],
        fg=theme['fg'],
        activebackground=theme['activebackground'],
        selectcolor=theme['selectcolor'],
        activeforeground=theme['fg'],
        disabledforeground=theme['fg'],
        anchor='w',
        **base_widget_attributes,
        **kwargs
    )


def default_separator(master, span=5, **kwargs):
    sep1 = tk.Frame(master, bg=theme['separator_bg1'],
                    height=1, borderwidth=1, relief="flat")
    sep2 = tk.Frame(master, bg=theme['separator_bg2'],
                    height=1, borderwidth=1, relief="flat")
    
    sep1.grid(row=0, column=0, sticky='ew', columnspan=span)
    sep2.grid(row=1, column=0, sticky='ew', columnspan=span)
    
    return sep1, sep2


def default_canvas(master, **kwargs):
    return tk.Canvas(master, bg=theme['bg'],
                    **base_widget_attributes, **kwargs)


def default_frame(master, **kwargs):
    return tk.Frame(master, bg=theme['bg'],
                    **base_widget_attributes, **kwargs)


def default_label(master, *args, **kwargs):
    # Accepts 'offline' as a custom argument to mute the text color
    fg_color = theme['offline_fg'] if 'offline' in args else theme['fg']
    return tk.Label(master, bg=theme['bg'], fg=fg_color,
                    **base_widget_attributes, **kwargs)


def default_button(master, *args, **kwargs):
    # Accepts 'offline' as a custom argument to mute the text color
    fg_color = theme['offline_fg'] if 'offline' in args else theme['fg']
    return tk.Button(
        master,
        bg=theme['bg'],
        fg=fg_color,
        activebackground=theme['activebackground'],
        activeforeground=theme['fg'],
        disabledforeground=fg_color,
        **base_widget_attributes,
        **kwargs
    )


def default_entry(master, *args, **kwargs):
    entry_theme = theme['entry']
    fg_color = entry_theme['offline_fg'] if 'offline' in args else entry_theme['fg']
    return tk.Entry(
        master,
        bg=entry_theme['bg'],
        fg=fg_color,
        disabledforeground=fg_color,
        insertbackground=entry_theme['cursor_color'],
        **base_widget_attributes,
        **kwargs
    )


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


# Add and edit color schemes here:
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
            'offline_fg': '#A4A4A4',
            'cursor_color': '#FFFFFF',
        },
        'scrollbar': {
            'bg': '#2c2c2c',
            'trough': '#363636',
            'arrow': '#BDBDBD',
            'active': '#222222'
        },
        'icon_ending': '_light'
    },
    'gnome_light': {
        'bg': '#FAFAFA',
        'fg': '#101010',
        'offline_fg': '#333333',
        'activebackground': '#EAEAEA',
        'selectcolor': '#FAFAFA',
        'separator_bg1': '#E3E3E3',
        'separator_bg2': '#FFFFFF',
        'entry': {
            'bg': '#E1E1E1',
            'fg': '#101010',
            'offline_fg': '#333333',
            'cursor_color': '#000000',
        },
        'scrollbar': {
            'bg': '#EFEFEF',
            'trough': '#DBDBDB',
            'arrow': '#2c2c2c',
            'active': '#FFFFFF'
        },
        'icon_ending': ''
    },
    'blues_dark': {
        'bg': '#30343F',
        'fg': '#B0B7BF',
        'offline_fg': '#9CA3AF',
        'activebackground': '#39404F',
        'selectcolor': '#24292F',
        'separator_bg1': '#262A34',
        'separator_bg2': '#4B515F',
        'entry': {
            'bg': '#414550',
            'fg': '#B0B7BF',
            'offline_fg': '#9CA3AF',
            'cursor_color': '#E3E3BD',
        },
        'scrollbar': {
            'bg': '#2F3441',
            'trough': '#3A3F4C',
            'arrow': '#D27F7F',
            'active': '#5A6E73'
        },
        'icon_ending': '_yellow'
    },
    'blues_light': {
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
            'offline_fg': '#2B3B52',
            'cursor_color': '#0D1B2A',
        },
        'scrollbar': {
            'bg': '#D4E8F1',
            'trough': '#BED5DC',
            'arrow': '#8A9BAA',
            'active': '#487A8B'
        },
        'icon_ending': ''
    },
    'reds_dark': {
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
            'offline_fg': '#A4A4A4',
            'cursor_color': '#FFFFFF',
        },
        'scrollbar': {
            'bg': '#3A2C2C',
            'trough': '#4A2C2C',
            'arrow': '#D15656',
            'active': '#8A3F3F'
        },
        'icon_ending': '_light'
    },
    'reds_light': {
        'bg': '#FFEDED',
        'fg': '#101010',
        'offline_fg': '#3B2B2B',
        'activebackground': '#F7DCDC',
        'selectcolor': '#FFA8A8',
        'separator_bg1': '#F4CFCF',
        'separator_bg2': '#FFE0E0',
        'entry': {
            'bg': '#F8D8D8',
            'fg': '#101010',
            'offline_fg': '#3B2B2B',
            'cursor_color': '#101010',
        },
        'scrollbar': {
            'bg': '#FDD5D5',
            'trough': '#F4BFBF',
            'arrow': '#BF3030',
            'active': '#E57373'
        },
        'icon_ending': ''
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
            'offline_fg': '#555555',
            'cursor_color': '#FFFFFF',
        },
        'scrollbar': {
            'bg': '#555555',
            'trough': '#1d1d1d',
            'arrow': '#252525',
            'active': '#353535'
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
current_theme = settings.get_setting('theme')
# Retrieves colors from dictionary:
theme = properties[current_theme]