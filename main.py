#!/usr/bin/env python

import subprocess
import re
import tkinter as tk
from tkinter.messagebox import askyesno
from tkinter.messagebox import showinfo
from tkinter.messagebox import showerror
from tkinter.simpledialog import askstring

def call_wtwitch():
    '''Run wtwitch c and use regex to extract all streamers and their online
    status. Return lists for both, along with online streamer information.
    '''
    wtwitch_c = subprocess.run(['wtwitch', 'c'],
                        capture_output=True,
                        text=True
                        )
    global wtwitch_c_full
    wtwitch_c_full = repr(wtwitch_c.stdout)
    off_streamers1 = re.findall(r'\[90m(\S*)\x1b', wtwitch_c.stdout)
    off_streamers2 = re.findall(r'\[90m(\S*),', wtwitch_c.stdout)
    offline_streamers = off_streamers1 + off_streamers2
    offline_streamers.sort()
    online_streamers = re.findall(r'\[92m(\S*)\x1b', wtwitch_c.stdout)
    stream_titles = re.findall(r'\[0m: (\S.*)\s\x1b\[93m\(', wtwitch_c.stdout)
    stream_categs = re.findall(r'\[93m\((\S.*)\)\x1b\[0m\n', wtwitch_c.stdout)
    return online_streamers, offline_streamers, stream_titles, stream_categs

def check_status():
    '''Call wtwitch c again when pressing the refresh button
    '''
    global status
    status = call_wtwitch()

def fetch_vods(streamer):
    '''Run wtwitch v and extract all timestamps/titles of the streamer's VODs
    with regex. Cap the title length at 70 characters.
    '''
    wtwitch_v = subprocess.run(['wtwitch', 'v', streamer],
                        capture_output=True,
                        text=True
                        )
    timestamps = re.findall(r'\[96m\[(\S* \d.*:\d.*):\d.*\]', wtwitch_v.stdout)
    titles = re.findall(r'\]\x1b\[0m\s*(\S.*)\s\x1b\[93m', wtwitch_v.stdout)
    length = re.findall(r'\x1b\[93m(\S*)\x1b\[0m', wtwitch_v.stdout)
    for i in range(len(titles)):
        if len(titles[i]) > 50:
            titles[i] = titles[i][:50] + "..."
    return timestamps, titles, length

def vod_panel_buttons(streamer):
    '''Shows a streamer's VODs inside the vod_frame on the right side of the
    window. Three for-loops to draw the timestamps, watch buttons and titles
    of the last 20 VODs
    '''
    # Clear the vod_panel before redrawing it, in case it was already opened
    vod_frame.forget()
    vod_frame.destroy()
    parent = vod_panel()
    root.geometry("")
    # Close button recalls this function and returns without drawing content:
    if streamer == "close_the_panel":
        return
    close_button = tk.Button(parent, image=close_icon, relief='flat',
                        command=lambda s="close_the_panel":
                        vod_panel_buttons(s)
                        )
    close_button.grid(column=2, row=0, sticky='ne', padx=5)
    # Retrieve the streamer's VODs:
    vods = fetch_vods(streamer)
    # Attach label with streamer name to the top left:
    vods_label = tk.Label(parent, text=f"{streamer}'s VODs:",
                        font=('Cantarell', '9'))
    vods_label.grid(column=2, row=0, sticky='w', pady=10, padx=5)
    # Account for streamers having no VODs:
    if len(vods[0]) == 0:
        warning_l = tk.Label(parent, text=f"{streamer} has no VODs")
        warning_l.grid(column=0, row=1, ipadx=10, ipady=10)
    # The three for-loops:
    vod_number = 1
    for timestamp in vods[0]:
        time_l = tk.Label(parent, text=timestamp, font=('', '8'))
        time_l.grid(column=0, row=vod_number, padx=5)
        vod_number += 1
    vod_number = 1
    for title in vods[1]:
        watch_b = tk.Button(parent,
                        image=play_icon,
                        relief='flat',
                        command=lambda s=streamer, v=vod_number:
                        [subprocess.run(['wtwitch', 'v', s, str(v)])]
                        )
        watch_b.grid(column=1, row=vod_number, sticky='w', ipadx=10)
        vod_number += 1
    vod_number = 1
    for title, length in zip(vods[1], vods[2]):
        title_l = tk.Label(parent, text=title + ' ' + length,
                        font=('Cantarell', '9')
                        )
        title_l.grid(column=2, row=vod_number, sticky='nw', ipadx=5)
        vod_number += 1

def streamer_buttons(parent, onoff):
    global count_rows
    if onoff == 0:
        streamer_list = status[0]
        image = streaming_icon
        state = 'normal'
    elif onoff == 1:
        streamer_list = status[1]
        image = offline_icon
        state = 'disabled'
    for index, streamer in enumerate(streamer_list):
        if onoff == 0:
            watch_button = tk.Button(parent, image=image,
                        relief='flat', height=27,
                        command=lambda s=streamer:
                        [subprocess.run(['wtwitch', 'w', s])]
                        )
        else:
            watch_button = tk.Label(parent, image=image)
        watch_button.grid(column=0, row=count_rows)
        info_button = tk.Button(parent,
                        text=streamer,
                        anchor='w', #justify='left',
                        font=('Cantarell', '11', 'bold'),
                        state=state, relief='flat',
                        width=15,
                        disabledforeground='#464646',
                        command=lambda i=index, s=streamer:
                        info_dialog(i, s)
                        )
        info_button.grid(column=1, row=count_rows)
        unfollow_b = tk.Button(parent,
                        image=unfollow_icon,
                        relief='flat',
                        height=27, width=20,
                        command=lambda s=streamer:
                        [unfollow_dialog(s)]
                        )
        unfollow_b.grid(column=2, row=count_rows)
        vod_b = tk.Button(parent,
                        image=vod_icon,
                        relief='flat',
                        height=27, width=20,
                        command=lambda s=streamer:
                        vod_panel_buttons(s)
                        )
        vod_b.grid(column=3, row=count_rows)
        count_rows += 1

def info_dialog(index, streamer):
    '''Info dialog, including stream title and stream category
    '''
    info = showinfo(title=f"{streamer} is streaming:",
                        message=f"{status[2][index]} ({status[3][index]})",
                        parent=root
                        )

def unfollow_dialog(streamer):
    '''Asks for confirmation, if the unfollow button is pressed. Rebuild the
    main panel, if confirmed.
    '''
    answer = askyesno(title='Unfollow',
                        message='Are you sure that you '
                                f'want to unfollow {streamer}?',
                        default='no',
                        parent=root
                        )
    if answer:
        update = subprocess.run(['wtwitch', 'u', streamer],
                        capture_output=True,
                        text=True
                        )
        refresh_main_panel()

def follow_dialog():
    '''Opens a text dialog and adds the entered string to the follow list.
    '''
    streamer = askstring(title='Follow',
                        prompt='Enter streamer name: ',
                        parent=root
                        )
    if streamer is None or len(streamer) <= 2:
        return
    else:
        update = subprocess.run(['wtwitch', 's', streamer],
                        capture_output=True,
                        text=True
                        )
        refresh_main_panel()

def vod_panel():
    '''Create the vod frame separately to avoid adding a new one, when the
    main panel gets refreshed.
    '''
    global vod_frame
    vod_frame = tk.Frame(root)
    vod_frame.pack(side='right', anchor='ne', pady=10, padx=5)
    return vod_frame

def refresh_main_panel():
    '''Runs wtwitch c and then rebuilds the main panel.
    '''
    check_status()
    panel_frame.pack_forget()
    panel_frame.destroy()
    main_panel()
    root.geometry("")

def main_panel():
    '''Always active after window start.
    '''
    global panel_frame
    panel_frame = tk.Frame(root)
    panel_frame.pack(side='left', anchor='nw', fill='x', padx=10, pady=10)
    global count_rows
    count_rows = 0
    streamer_buttons(panel_frame, 0)
    streamer_buttons(panel_frame, 1)

def custom_player():
    '''Opens a dialog to set a custom media player.
    '''
    player = askstring(title='Player',
                        prompt='Enter your media player:',
                        parent=root)
    if player is None or len(player) == 0:
        return
    else:
        confirmation = subprocess.run(['wtwitch', 'p', player],
                        text=True,
                        capture_output=True
                        )
        confirmation = re.findall(r'\n\\s(.*)\n\x1b\[0m', confirmation.stdout)
        return showinfo(title='Player',
                        message=confirmation[0],
                        parent=root)

def custom_quality():
    '''Opens a dialog to set a custom stream quality.
    '''
    new_quality = askstring(title='Quality',
                        prompt= '\n Options: 1080p60, 720p60, 720p, 480p, \n'
                                ' 360p, 160p, best, worst, and audio_only \n'
                                '\n'
                                ' Specify fallbacks separated by a comma: \n'
                                ' E.g. "720p,480p,worst" \n',
                        parent=root)
    if new_quality is None or len(new_quality) == 0:
        return
    else:
        set_quality = subprocess.run(['wtwitch', 'q', new_quality],
                        text=True,
                        capture_output=True
                        )
        confirmation = re.findall(r'\n\s(.*)\n\x1b\[0m', set_quality.stdout)
        if len(confirmation) >= 1:
            return showinfo(title='Quality',
                        message=confirmation[0],
                        parent=root)
            current_quality = new_quality
        else:
            error = re.findall(r'\[0m: (\S.*?\.)', set_quality.stderr)
            return showerror(title='Error',
                        message=error[0],
                        parent=root)

def menu_bar():
    '''The entire menu bar of the root window.
    '''
    font = ('Cantarell', '10')
    font2 = ('Cantarell', '10', 'bold')
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    menubar.add_command(label='Refresh', font=font2,
            command=lambda: refresh_main_panel())
    menubar.add_command(label='Follow streamer', font=font,
            command=lambda: follow_dialog())
    # Options drop-down menu:
    options_menu = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(label='Options', menu=options_menu, font=font)
    # Sub-menu for quality options:
    quality_menu = tk.Menu(options_menu, tearoff=False)
    options_menu.add_cascade(label='Quality', menu=quality_menu, font=font)
    quality_menu.add_command(label='High', font=font,
            command=lambda: subprocess.run(['wtwitch', 'q', 'best']))
    quality_menu.add_command(label='Medium', font=font,
            command=lambda:
            subprocess.run(['wtwitch', 'q', '720p,720p60,480p,best']))
    quality_menu.add_command(label='Low', font=font,
            command=lambda: subprocess.run(['wtwitch', 'q', 'worst']))
    quality_menu.add_separator()
    quality_menu.add_command(label='Custom', font=font,
            command=lambda: custom_quality())
    # Sub-menu for player options:
    player_menu = tk.Menu(options_menu, tearoff=False)
    options_menu.add_cascade(label='Player', menu=player_menu)
    player_menu.add_command(label='mpv', font=font,
            command=lambda: subprocess.run(['wtwitch', 'p', 'mpv']))
    player_menu.add_command(label='VLC', font=font,
            command=lambda: subprocess.run(['wtwitch', 'p', 'vlc']))
    player_menu.add_separator()
    player_menu.add_command(label='Custom', font=font,
            command=lambda: custom_player())

def toggle_color():
    wtwitch_l = subprocess.run(['wtwitch', 'l'],
                        capture_output=True,
                        text=True
                        )
    if not re.search('\\[32m', wtwitch_l.stdout):
        toggle_color()
    else:
        return

# Check the online/offline status once before window initialization:
status = call_wtwitch()

# Make sure that colors in the terminal output are activated:
toggle_color()

# Create the main window
root = tk.Tk()
root.title("GUI for wtwitch")

# Import icons:
unfollow_icon = tk.PhotoImage(file='icons/unfollow_icon.png')
info_icon = tk.PhotoImage(file='icons/info_icon.png')
empty_icon = tk.PhotoImage(file='icons/empty_icon.png')
vod_icon = tk.PhotoImage(file='icons/vod_icon.png')
streaming_icon = tk.PhotoImage(file='icons/streaming_icon.png')
offline_icon = tk.PhotoImage(file='icons/offline_icon.png')
play_icon = tk.PhotoImage(file='icons/play_icon.png')
close_icon = tk.PhotoImage(file='icons/close_icon.png')

app_icon = tk.PhotoImage(file='icons/app_icon.png')
root.wm_iconphoto(False, app_icon)

menu_bar()
main_panel()
vod_panel()
root.mainloop()