#!/usr/bin/env python

import subprocess
import re
import tkinter as tk
from tkinter.messagebox import askyesno
from tkinter.messagebox import showinfo
from tkinter import simpledialog

def call_wtwitch():
    '''Run wtwitch c and use regex to extract all streamers and their online
    status. Return lists for both, along with online streamer information.
    '''
    wtwitch_c = subprocess.run(['wtwitch', 'c'],
                            capture_output=True,
                            text=True
                            )
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
    timestamps = re.findall('\[96m\[(\S* \S*)\]', wtwitch_v.stdout)
    titles = re.findall('\]\x1b\[0m\s*(\S.*)\s\x1b\[93m', wtwitch_v.stdout)
    for i in range(len(titles)):
        if len(titles[i]) > 60:
            titles[i] = titles[i][:60] + "..."
    return timestamps, titles

def vod_panel_buttons(streamer):
    '''Draws the VOD panel inside the vod_frame on the right side of the
    window. Three for-loops to draw the timestamps, watch buttons and titles
    of the last 20 VODs
    '''
    # Clear the vod_panel before redrawing it, in case it was already opened
    vodframe.forget()
    vodframe.destroy()
    parent = vod_panel()
    root.geometry("")
    # Close button recalls this function and returns without drawing content:
    if streamer == "close_the_panel":
        return
    close_button = tk.Button(parent, text='x',
                        command=lambda s="close_the_panel":
                        vod_panel_buttons(s)
                        )
    close_button.grid(column=2, row=0, sticky='ne')
    # Retreive the streamer's VODs:
    vods = fetch_vods(streamer)
    # Attach label with streamer name to the top left:
    vods_label = tk.Label(parent, text=f"{streamer}'s VODs:")
    vods_label.grid(column=0, row=0, sticky='nw', ipadx=30, ipady=10)
    # Account for streamer having no VODs:
    if len(vods[0]) == 0:
        warning_l = tk.Label(parent, text=f"{streamer} has no VODs")
        warning_l.grid(column=0, row=1, ipadx=10, ipady=10)
    # The three for-loops:
    vodno = 1
    for timestamp in vods[0]:
        time_l = tk.Label(parent, text=timestamp)
        time_l.grid(column=0, row=vodno, sticky='e', ipadx=20)
        vodno += 1
    vodno = 1
    for title in vods[1]:
        watch_b = tk.Button(parent,
                    text="Watch",
                    command=lambda s=streamer, vodno=vodno:
                    [subprocess.run(['wtwitch', 'v', s, str(vodno)])]
                    )
        watch_b.grid(column=1, row=vodno, ipadx=12)
        vodno += 1
    vodno = 1
    for title in vods[1]:
        title_l = tk.Label(parent, text=title)
        title_l.grid(column=2, row=vodno, sticky='w', ipadx=20)
        vodno += 1

def section_label(parent, text):
    '''Create text labels for window sections
    '''
    label = tk.Label(parent, text=text, justify='left', anchor='s')
    label.pack(ipady=10, ipadx=10, anchor='sw')

def streamer_buttons(parent, onoff, state):
    '''Create two rows of buttons. On the left the streamers (disabled if
    offline) and on the right their respective VOD buttons
    '''
    streamers = tk.Frame(parent, pady=10)
    streamers.pack(side='left')
    for streamer in status[onoff]:
        watch_b = tk.Button(streamers,
                            text=streamer,
                            justify='left',
                            padx=15,
                            font=('Cantarell', '11', 'bold'),
                            anchor='w',
                            state=state,
                            width=15,
                            disabledforeground='#464646',
                            command=lambda s=streamer:
                            [subprocess.run(['wtwitch', 'w', s])]
                            )
        watch_b.pack(fill='x', side='top')
    # VOD Buttons:
    vods = tk.Frame(parent, pady=10)
    vods.pack(side='right')
    for streamer in status[onoff]:
        vod_b = tk.Button(vods,
                        text="Vods",
                        justify='right',
                        font=('Cantarell', '11'),
                        command=lambda s=streamer:
                        vod_panel_buttons(s)
                        )
        vod_b.pack(fill='x', side='top')

def info_buttons(topframe):
    '''Adds info buttons for every streamer, to show and info dialog with the
    stream title and stream category.
    '''
    info_box = tk.Frame(topframe, pady=10)
    info_box.pack(side='left')
    for index, streamer in enumerate(status[0]):
        info_b = tk.Button(info_box,
                            text="Info",
                            justify='left',
                            font=('Cantarell', '11'),
                            command=lambda i=index, s=streamer:
                            info_dialog(i, s)
                            )
        info_b.pack(fill='x', side='top')

def info_dialog(index, streamer):
    '''Info dialog, including stream title and stream category
    '''
    info = showinfo(title=f"{streamer} is streaming:",
                    message=f"{status[2][index]} ({status[3][index]})")

def unfollow_buttons(frame, onoff):
    '''Adds unfollow buttons for every streamer.
    '''
    unfollow = tk.Frame(frame, pady=10)
    unfollow.pack(side='right')
    for streamer in status[onoff]:
        unfollow_b = tk.Button(unfollow,
                            text="U",
                            justify='left',
                            font=('Cantarell', '11'),
                            command=lambda s=streamer:
                            [unfollow_confirmation(s)]
                            )
        unfollow_b.pack(fill='x', side='top')

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
        panelframe.pack_forget()
        main_panel()

def follow_dialog():
    '''Opens a text dialog and adds the entered string to the follow list.
    '''
    streamer = simpledialog.askstring(title='Follow',
                                prompt='Enter streamer name: ',
                                parent=panelframe)
    if streamer is None:
        return
    elif len(streamer) > 0:
        subprocess.run(['wtwitch', 's', streamer])
        check_status()
        panelframe.pack_forget()
        main_panel()
    else:
        return

def vod_panel():
    '''Create the vod frame separately to avoid adding a new one, when the
    main panel gets refreshed.
    '''
    global vodframe
    vodframe = tk.Frame(root)
    vodframe.pack(side='right', anchor='nw', fill='x', pady=10)
    return vodframe

def refresh_panelframe():
    '''Runs wtwitch c and then rebuilds the main panel.
    '''
    check_status()
    panelframe.pack_forget()
    panelframe.destroy()
    main_panel()
    root.geometry("")

def main_panel():
    '''Always active after window start. Segmented into a top and bottom frame
    for online and offline streamers
    '''
    global panelframe
    panelframe = tk.Frame(root)
    panelframe.pack(side='left', anchor='nw', fill='x')
    # Create section of online streamers with 'watch' and VOD buttons:
    topframe = tk.Frame(panelframe)
    topframe.pack(side='top', fill='x')
    section_label(topframe, 'Online: ')
    streamer_buttons(topframe, 0, 'normal')
    info_buttons(topframe)
    unfollow_buttons(topframe, 0)
    # Create offline streamer section with VOD buttons:
    bottomframe = tk.Frame(panelframe)
    bottomframe.pack(side='bottom', fill='x')
    section_label(bottomframe, 'Offline: ')
    streamer_buttons(bottomframe, 1, 'disabled')
    unfollow_buttons(bottomframe, 1)

def menu_bar():
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    menubar.add_command(
            label='Refresh',
            command=lambda: refresh_panelframe())
    menubar.add_command(
            label='Follow streamer',
            command=lambda: follow_dialog())

# Check the online/offline status once before window initialization:
status = call_wtwitch()
# Create the main window
root = tk.Tk()
root.title("GUI for wtwitch")
menu_bar()
main_panel()
vod_panel()
root.mainloop()