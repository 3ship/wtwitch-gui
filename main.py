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
    wtwitch_c_full = wtwitch_c.stdout
    off_streamers1 = re.findall('\[90m(\S*)\x1b', wtwitch_c.stdout)
    off_streamers2 = re.findall('\[90m(\S*),', wtwitch_c.stdout)
    offline_streamers = off_streamers1 + off_streamers2
    offline_streamers.sort()
    online_streamers = re.findall('\[92m(\S*)\x1b', wtwitch_c.stdout)
    stream_titles = re.findall('\[0m: (\S.*)\s\x1b\[93m\(', wtwitch_c.stdout)
    stream_categs = re.findall('\[93m\((\S.*)\)\x1b\[0m\n', wtwitch_c.stdout)
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
    timestamps = re.findall('\[96m\[(\S* \d.*:\d.*):\d.*\]', wtwitch_v.stdout)
    titles = re.findall('\]\x1b\[0m\s*(\S.*)\s\x1b\[93m', wtwitch_v.stdout)
    length = re.findall('\x1b\[93m(\S*)\x1b\[0m', wtwitch_v.stdout)
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
    close_button = tk.Button(parent, text='\U0001F5D9', relief='ridge',
                        command=lambda s="close_the_panel":
                        vod_panel_buttons(s)
                        )
    close_button.grid(column=2, row=0, sticky='ne')
    # Retrieve the streamer's VODs:
    vods = fetch_vods(streamer)
    # Attach label with streamer name to the top left:
    vods_label = tk.Label(parent, text=f"{streamer}'s VODs:")
    vods_label.grid(column=0, row=0, sticky='nw', ipadx=30, ipady=10)
    # Account for streamers having no VODs:
    if len(vods[0]) == 0:
        warning_l = tk.Label(parent, text=f"{streamer} has no VODs")
        warning_l.grid(column=0, row=1, ipadx=10, ipady=10)
    # The three for-loops:
    vod_number = 1
    for timestamp in vods[0]:
        time_l = tk.Label(parent, text=timestamp)
        time_l.grid(column=0, row=vod_number, sticky='e', ipadx=10)
        vod_number += 1
    vod_number = 1
    for title in vods[1]:
        watch_b = tk.Button(parent,
                    text='\U000025B6',
                    relief='flat',
                    command=lambda s=streamer, v=vod_number:
                    [subprocess.run(['wtwitch', 'v', s, str(v)])]
                    )
        watch_b.grid(column=1, row=vod_number, ipadx=10)
        vod_number += 1
    vod_number = 1
    for title, length in zip(vods[1], vods[2]):
        title_l = tk.Label(parent, text=title + ' ' + length)
        title_l.grid(column=2, row=vod_number, sticky='w', ipadx=10)
        vod_number += 1

def streamer_buttons(parent, onoff, state):
    '''Create two rows of buttons. On the left the streamers (disabled if
    offline) and on the right their respective VOD buttons
    '''
    if onoff == 0:
        s_icon = '\U0001F7E2  '
    elif onoff == 1:
        s_icon = '\U0001F534  '
    count = 0
    for streamer in status[onoff]:
        status_icon = tk.Button(parent,
                            text=s_icon,
                            relief='flat',
                            state='disabled')
        status_icon.grid(column=0, row=count)
        count += 1
    count = 0
    for streamer in status[onoff]:
        watch_b = tk.Button(parent,
                            text=streamer,
                            justify='left',
                            padx=5,
                            font=('Cantarell', '11', 'bold'),
                            anchor='w',
                            state=state,
                            width=15,
                            relief='flat',
                            disabledforeground='#464646',
                            command=lambda s=streamer:
                            [subprocess.run(['wtwitch', 'w', s])]
                            )
        watch_b.grid(column=1, row=count)
        count += 1
    # VOD Buttons:
    count = 0
    for streamer in status[onoff]:
        vod_b = tk.Button(parent,
                        text='\U0001F4FC',
                        justify='right',
                        relief='flat',
                        font=('Cantarell', '11'),
                        command=lambda s=streamer:
                        vod_panel_buttons(s)
                        )
        vod_b.grid(column=4, row=count)
        count += 1

def info_buttons(parent, onoff):
    '''Adds info buttons for every streamer, to show and info dialog with the
    stream title and stream category.
    '''
    count = 0
    if onoff == 0:
        for index, streamer in enumerate(status[0]):
            info_b = tk.Button(parent,
                            text='\U00002139',
                            justify='left',
                            relief='flat',
                            font=('Cantarell', '11'),
                            command=lambda i=index, s=streamer:
                            info_dialog(i, s)
                            )
            info_b.grid(column=2, row=count)
            count += 1
    elif onoff == 1:
        for streamer in status[1]:
            info_b = tk.Button(parent,
                            text='\U00002139',
                            justify='left',
                            relief='flat',
                            state='disabled',
                            font=('Cantarell', '11'),
                            )
            info_b.grid(column=2, row=count)
            count += 1


def info_dialog(index, streamer):
    '''Info dialog, including stream title and stream category
    '''
    info = showinfo(title=f"{streamer} is streaming:",
                    message=f"{status[2][index]} ({status[3][index]})")

def unfollow_buttons(parent, onoff):
    '''Adds unfollow buttons for every streamer.
    '''
    count = 0
    for streamer in status[onoff]:
        unfollow_b = tk.Button(parent,
                            text="\U0000274C",
                            justify='left',
                            relief='flat',
                            font=('Cantarell', '11'),
                            command=lambda s=streamer:
                            [unfollow_confirmation(s)]
                            )
        unfollow_b.grid(column=3, row=count)
        count += 1

def unfollow_confirmation(streamer):
    '''Asks for confirmation, if the unfollow button is pressed. Rebuild the
    main panel, if confirmed.
    '''
    answer = askyesno(title='Unfollow',
            message=f'Are you sure that you want to unfollow {streamer}?',
            default='no')
    if answer:
        subprocess.run(['wtwitch', 'u', streamer])
        check_status()
        panel_frame.pack_forget()
        main_panel()

def follow_dialog():
    '''Opens a text dialog and adds the entered string to the follow list.
    '''
    streamer = askstring(title='Follow',
                        prompt='Enter streamer name: ',
                        parent=panel_frame)
    if streamer is None or len(streamer) == 0:
        return
    else:
        subprocess.run(['wtwitch', 's', streamer])
        check_status()
        panel_frame.pack_forget()
        main_panel()

def vod_panel():
    '''Create the vod frame separately to avoid adding a new one, when the
    main panel gets refreshed.
    '''
    global vod_frame
    vod_frame = tk.Frame(root)
    vod_frame.pack(side='right', anchor='nw', fill='x', pady=10, padx=5)
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
    '''Always active after window start. Segmented into a top and bottom frame
    for online and offline streamers
    '''
    global panel_frame
    panel_frame = tk.Frame(root)
    panel_frame.pack(side='left', anchor='nw', fill='x', padx=10)
    # Create section of online streamers with 'watch' and VOD buttons:
    top_frame = tk.Frame(panel_frame)
    top_frame.pack(side='top', fill='x')
    streamer_buttons(top_frame, 0, 'normal')
    info_buttons(top_frame, 0)
    unfollow_buttons(top_frame, 0)
    # Create offline streamer section with VOD buttons:
    bottom_frame = tk.Frame(panel_frame)
    bottom_frame.pack(side='bottom', fill='x')
    streamer_buttons(bottom_frame, 1, 'disabled')
    info_buttons(bottom_frame, 1)
    unfollow_buttons(bottom_frame, 1)

def custom_player():
    '''Opens a dialog to set a custom media player.
    '''
    player = askstring(title='Player',
                        prompt='Enter your media player:',
                        parent=panel_frame)
    if player is None or len(player) == 0:
        return
    else:
        confirmation = subprocess.run(['wtwitch', 'p', player],
                                        text=True,
                                        capture_output=True)
        confirmation = re.findall('\n\s(.*)\n\x1b\[0m', confirmation.stdout)
        return showinfo(title='Quality',
                        message=confirmation[0])

def custom_quality():
    '''Opens a dialog to set a custom stream quality.
    '''
    current_quality = re.findall('Quality set to (\S.*)', wtwitch_c_full)
    new_quality = askstring(title='Quality',
                        prompt= '\n Options: 1080p60, 720p60, 720p, 480p, \n'
                                ' 360p, 160p, best, worst, and audio_only \n'
                                '\n'
                                ' Specify fallbacks separated by a comma: \n'
                                ' E.g. "720p,480p,worst" \n',
                        initialvalue=current_quality[0],
                        parent=panel_frame)
    if new_quality is None or len(new_quality) == 0:
        return
    else:
        set_quality = subprocess.run(['wtwitch', 'q', new_quality],
                                        text=True,
                                        capture_output=True)
        confirmation = re.findall('\n\s(.*)\n\x1b\[0m', set_quality.stdout)
        if len(confirmation) >= 1:
            return showinfo(title='Quality',
                        message=confirmation[0])
            current_quality = new_quality
        else:
            error = re.findall('\[0m: (.*quality\.)', set_quality.stderr)
            return showerror(title='Error',
                        message=error[0])

def menu_bar():
    '''The entire menu bar of the root window.
    '''
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    menubar.add_command(label='Refresh',
            command=lambda: refresh_main_panel())
    menubar.add_command(label='Follow streamer',
            command=lambda: follow_dialog())
    # Options drop-down menu:
    options_menu = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(label='Options', menu=options_menu)
    # Sub-menu for quality options:
    quality_menu = tk.Menu(options_menu, tearoff=False)
    options_menu.add_cascade(label='Quality', menu=quality_menu)
    quality_menu.add_command(label='High',
            command=lambda: subprocess.run(['wtwitch', 'q', 'best']))
    quality_menu.add_command(label='Medium',
            command=lambda:
            subprocess.run(['wtwitch', 'q', '720p,720p60,480p,best']))
    quality_menu.add_command(label='Low',
            command=lambda: subprocess.run(['wtwitch', 'q', 'worst']))
    quality_menu.add_separator()
    quality_menu.add_command(label='Custom',
            command=lambda: custom_quality())
    # Sub-menu for player options:
    player_menu = tk.Menu(options_menu, tearoff=False)
    options_menu.add_cascade(label='Player', menu=player_menu)
    player_menu.add_command(label='mpv',
            command=lambda: subprocess.run(['wtwitch', 'p', 'mpv']))
    player_menu.add_command(label='VLC',
            command=lambda: subprocess.run(['wtwitch', 'p', 'vlc']))
    player_menu.add_separator()
    player_menu.add_command(label='Custom',
            command=lambda: custom_player())

def toggle_color():
    wtwitch_l = subprocess.run(['wtwitch', 'l'],
                            capture_output=True,
                            text=True)
    if re.search('Turned colors on.', wtwitch_l.stdout):
        return
    else:
        toggle_color()

# Check the online/offline status once before window initialization:
status = call_wtwitch()
# Make sure that colors in the terminal output are activated:
toggle_color()
# Create the main window
root = tk.Tk()
root.title("GUI for wtwitch")
"""sb = tk.Scrollbar(root)
sb.pack(side='right', fill ='y')
c = tk.Canvas(root, yscrollcommand=sb.set)
c.pack(side='top', fill='x')
sb.config(command=c.yview)"""
menu_bar()
main_panel()
vod_panel()
root.mainloop()