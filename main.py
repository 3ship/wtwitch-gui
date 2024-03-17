#!/usr/bin/env python

import subprocess
import re
import tkinter as tk
from tkinter import ttk
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
    with regex. Cap the title length at 50 characters.
    '''
    wtwitch_v = subprocess.run(['wtwitch', 'v', streamer],
                        capture_output=True,
                        text=True
                        )
    timestamps = re.findall(r'\[96m\[(\S* \d.*:\d.*):\d.*\]', wtwitch_v.stdout)
    titles = re.findall(r'\]\x1b\[0m\s*(\S.*)\s\x1b\[93m', wtwitch_v.stdout)
    length = re.findall(r'\x1b\[93m(\S*)\x1b\[0m', wtwitch_v.stdout)
    #for i in range(len(titles)):
    #    if len(titles[i]) > 50:
    #        titles[i] = titles[i][:50] + "..."
    return timestamps, titles, length

def vod_panel(streamer):
    '''Draw 2 columns for the watch buttons and timestamps/stream length of
    the last 20 VODs.
    '''
    # Retrieve the streamer's VODs:
    vods = fetch_vods(streamer)
    # Account for streamer having zero VODs:
    if len(vods[0]) == 0:
        no_vods = showinfo(title=f"No VODs",
                        message=f"{streamer} has no VODs",
                        parent=root
                        )
        return
    # frame-canvas-frame to attach a scrollbar:
    vw_frame = tk.Frame(root)
    vw_frame.grid(column='0', row='1', sticky='nsew')
    vw_frame.columnconfigure(0, weight=1)
    vw_frame.rowconfigure(0, weight=1)
    vw_canvas = tk.Canvas(vw_frame)
    vw_scrollbar = ttk.Scrollbar(vw_frame,orient="vertical",
                        command=vw_canvas.yview
                        )
    vw_canvas.configure(yscrollcommand=vw_scrollbar.set)
    vod_frame = ttk.Frame(vw_frame, padding='10', relief='sunken')
    vod_frame.bind("<Configure>", lambda e:
                        vw_canvas.configure(
                        scrollregion=vw_canvas.bbox("all"))
                        )
    # Show streamer name and close button before the VODs
    vods_label = tk.Label(vod_frame, text=f"{streamer}'s VODs:",
                        font=('Cantarell', '9', 'bold'))
    vods_label.grid(column=1, row=0)
    close_button = tk.Button(vod_frame, image=close_icon, relief='flat',
                        command=lambda: [vw_frame.forget(), vw_frame.destroy()]
                        )
    close_button.grid(column=2, row=0, sticky='e')
    # Draw the VOD grid:
    vod_number = 1
    for timestamp, title, length in zip(vods[0], vods[1], vods[2]):
        watch_button = tk.Button(vod_frame,
                        image=play_icon,
                        relief='flat',
                        height='24', width='24',
                        command=lambda s=streamer, v=vod_number:
                        [subprocess.run(['wtwitch', 'v', s, str(v)])]
                        )
        watch_button.grid(column=0, row=vod_number, sticky='ew')
        timestamp_button = tk.Button(vod_frame, text=f"{timestamp} {length}",
                        command=lambda ts=timestamp, t=title, p=root:
                        showinfo(ts, t, parent=p),
                        font=('', '8'),
                        relief='flat',
                        width=25, anchor='w'
                        )
        timestamp_button.grid(column=1, row=vod_number, sticky='w')
        vod_number += 1
    # Finish the scrollbar
    vw_canvas.create_window((0, 0), window=vod_frame, anchor="nw")
    vw_canvas.grid(row=0, column=0, sticky="nsew", padx=8, pady=5)
    vw_scrollbar.grid(row=0, column=1, sticky="ns")
    vw_canvas.bind_all("<MouseWheel>", mouse_scroll)

def streamer_buttons(parent, onoff):
    ''' Draws rows of buttons/labels for each streamer into the main panel.
    Called two times to sort online before offline streamers.
    '''
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
                        anchor='w',
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
                        height=27, width=30,
                        command=lambda s=streamer:
                        vod_panel(s)
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

def refresh_main_panel():
    '''Runs wtwitch c and then rebuilds the main panel.
    '''
    check_status()
    main_frame.pack_forget()
    main_frame.destroy()
    main_window()

def mouse_scroll(event):
    meta_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def main_window():
    '''The main window. Calls streamer_buttons() twice, to draw buttons for
    online and offline streamers.
    '''
    # Create basis for scrollbar:
    meta_frame = ttk.Frame(root)
    meta_frame.grid(column='0', row='0', sticky='nsew')
    meta_canvas = tk.Canvas(meta_frame)
    scrollbar = ttk.Scrollbar(meta_frame,
                        orient="vertical", command=meta_canvas.yview)
    meta_canvas.configure(yscrollcommand=scrollbar.set)
    # Draw main content:
    global main_frame
    main_frame = ttk.Frame(meta_canvas)
    main_frame.bind("<Configure>", lambda e:
                        meta_canvas.configure(
                        scrollregion=meta_canvas.bbox("all"))
                        )
    global count_rows
    count_rows = 0
    streamer_buttons(main_frame, 0)
    streamer_buttons(main_frame, 1)
    # Finish scrollbar:
    meta_frame.columnconfigure(0, weight=1)
    meta_frame.rowconfigure(0, weight=1)
    meta_canvas.create_window((0, 0), window=main_frame, anchor="nw")
    meta_canvas.grid(row=0, column=0, sticky="nsew", pady=5, padx=5)
    scrollbar.grid(row=0, column=1, sticky="ns")
    meta_canvas.bind_all("<MouseWheel>", mouse_scroll)

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
    options_menu.add_cascade(label='Player', menu=player_menu, font=font)
    player_menu.add_command(label='mpv', font=font,
            command=lambda: subprocess.run(['wtwitch', 'p', 'mpv']))
    player_menu.add_command(label='VLC', font=font,
            command=lambda: subprocess.run(['wtwitch', 'p', 'vlc']))
    player_menu.add_separator()
    player_menu.add_command(label='Custom', font=font,
            command=lambda: custom_player())

def window_size():
    """Sets the default window length, depending on the number of streamers in
    the follow list, up to a maximum of 650 px.
    """
    window_width = "280"
    variable_height = len(status[0])*27+len(status[1])*27+100
    max_height = 650
    if variable_height > max_height:
        window_height = str(max_height)
    else:
        window_height = str(variable_height)
    return f"{window_width}x{window_height}"

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
root.geometry(window_size())
root.resizable(False, True)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Import icons:
unfollow_icon = tk.PhotoImage(file='icons/unfollow_icon.png')
vod_icon = tk.PhotoImage(file='icons/vod_icon.png')
streaming_icon = tk.PhotoImage(file='icons/streaming_icon.png')
offline_icon = tk.PhotoImage(file='icons/offline_icon.png')
play_icon = tk.PhotoImage(file='icons/play_icon.png')
close_icon = tk.PhotoImage(file='icons/close_icon.png')

app_icon = tk.PhotoImage(file='icons/app_icon.png')
root.wm_iconphoto(True, app_icon)

menu_bar()
main_window()
root.mainloop()