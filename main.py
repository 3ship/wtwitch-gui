#!/usr/bin/env python

import subprocess
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import encoded_images
import twitchapi

def vod_panel(streamer):
    '''Draw 2 columns for the watch buttons and timestamps/stream length of
    the last 20 VODs.
    '''
    # Retrieve the streamer's VODs:
    vods = twitchapi.fetch_vods(streamer)
    # Account for streamer having zero VODs:
    if len(vods[0]) == 0:
        no_vods = messagebox.showinfo(title=f"No VODs",
                        message=f"{streamer} has no VODs",
                        parent=root
                        )
        return
    # frame-canvas-frame to attach a scrollbar:
    close_button = tk.Button(
                        root,
                        image=close_icon,
                        relief='flat',
                        command=lambda: [vw_frame.forget(), vw_frame.destroy()]
                        )
    vw_frame = ttk.Labelframe(root, labelwidget=close_button)
    vw_frame.grid(column='0', row='1', sticky='nsew')
    vw_frame.columnconfigure(0, weight=1)
    vw_frame.rowconfigure(0, weight=1)
    met_frame = ttk.Frame(vw_frame)
    met_frame.grid(column='0', row='1', sticky='nsew')
    met_frame.columnconfigure(0, weight=1)
    met_frame.rowconfigure(0, weight=1)
    vw_canvas = tk.Canvas(met_frame)
    vw_scrollbar = ttk.Scrollbar(met_frame,orient="vertical",
                        command=vw_canvas.yview
                        )
    vw_canvas.configure(yscrollcommand=vw_scrollbar.set)
    vod_frame = ttk.Labelframe(met_frame,
                        text=f"{streamer}'s VODs",
                        )
    vod_frame.bind("<Configure>", lambda e:
                        vw_canvas.configure(
                        scrollregion=vw_canvas.bbox("all"))
                        )
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
        watch_button.grid(column=0, row=vod_number, sticky='nesw')
        timestamp_button = tk.Button(vod_frame, text=f"{timestamp} ({length})",
                        command=lambda ts=timestamp, t=title, p=root:
                        messagebox.showinfo("VOD", ts, detail=t, parent=p),
                        font=('', '10'),
                        relief='flat',
                        anchor='w'
                        )
        timestamp_button.grid(column=1, row=vod_number, sticky='nesw')
        vod_number += 1
    # Finish the scrollbar
    vw_canvas.create_window((0, 0), window=vod_frame, anchor="nw")
    vw_canvas.grid(row=0, column=0, sticky="nsew", padx=8, pady=5)
    vw_scrollbar.grid(row=0, column=1, sticky="ns")
    vw_canvas.bind_all("<MouseWheel>", mouse_scroll)

def streamer_buttons(parent):
    online_streamers = streamer_status[0]
    offline_streamers = streamer_status[1]
    count_rows = 0
    for package in online_streamers:
        watch_button = tk.Button(parent,
                        image=streaming_icon,
                        relief='flat',
                        command=lambda s=package[0]:
                        [subprocess.run(['wtwitch', 'w', s])]
                        )
        watch_button.grid(column=0, row=count_rows, sticky='ns')
        info_button = tk.Button(parent,
                        text=package[1],
                        anchor='w',
                        font=big_font,
                        relief='flat',
                        width=14,
                        command= lambda s=package[1], c=package[2],
                                        t=package[3], v=package[4]:
                                online_info(s, c, t, v)
                        )
        info_button.grid(column=1, row=count_rows, sticky='nesw')
        unfollow_b = tk.Button(parent,
                        image=unfollow_icon,
                        relief='flat',
                        command=lambda s=package[1]:
                        [unfollow_dialog(s)]
                        )
        unfollow_b.grid(column=2, row=count_rows, sticky='ns')
        vod_b = tk.Button(parent,
                        image=vod_icon,
                        relief='flat',
                        command=lambda s=package[1]:
                        vod_panel(s)
                        )
        vod_b.grid(column=3, row=count_rows, sticky='ns')
        count_rows += 1
    for streamer in offline_streamers:
        watch_button = tk.Button(parent,
                        image=offline_icon,
                        relief='flat',
                        command=lambda s=streamer:
                        [subprocess.run(['wtwitch', 'w', s])]
                        )
        watch_button.grid(column=0, row=count_rows, sticky='ns')
        info_button = tk.Button(parent,
                        text=streamer,
                        anchor='w',
                        font=bigbold_font,
                        fg='#474747',
                        relief='flat',
                        width=14,
                        compound='left',
                        disabledforeground='#464646',
                        command= lambda s=streamer:
                                offline_info(s)
                        )
        info_button.grid(column=1, row=count_rows, sticky='nesw')
        unfollow_b = tk.Button(parent,
                        image=unfollow_icon,
                        relief='flat',
                        command=lambda s=streamer:
                        [unfollow_dialog(s)]
                        )
        unfollow_b.grid(column=2, row=count_rows, sticky='ns')
        vod_b = tk.Button(parent,
                        image=vod_icon,
                        relief='flat',
                        command=lambda s=streamer:
                        vod_panel(s)
                        )
        vod_b.grid(column=3, row=count_rows, sticky='ns')
        count_rows += 1

def online_info(streamer, category, title, viewers):
    '''Info dialog, including stream title and stream category
    '''
    info = messagebox.showinfo(title=f"{streamer} is streaming",
                        message=category,
                        detail=f"{title}\n({viewers} viewers)",
                        parent=root,
                        )

def offline_info(streamer):
    info = messagebox.showinfo(title=f"{streamer} is offline",
                        message=f'Last seen: {twitchapi.last_seen(streamer)}',
                        parent=root,
                        )

def error_dialog():
    messagebox.showerror(title='Error',
                        message='Can\'t refresh Twitch data',
                        )

def unfollow_dialog(streamer):
    '''Asks for confirmation, if the unfollow button is pressed. Rebuild the
    main panel, if confirmed.
    '''
    answer = messagebox.askyesno(title='Unfollow',
                        message='Are you sure that you '
                                f'want to unfollow {streamer}?',
                        default='no',
                        parent=root
                        )
    if answer:
        twitchapi.unfollow_streamer(streamer)
        refresh_main()

def follow_dialog():
    '''Opens a text dialog and adds the entered string to the follow list.
    '''
    answer = simpledialog.askstring(title='Follow',
                        prompt='Enter streamer name: ',
                        parent=root
                        )
    if answer is None or len(answer) == 0:
        return
    else:
        twitchapi.follow_streamer(answer)
        refresh_main()

def play_dialog():
    '''Opens a text dialog to play a custom stream
    '''
    streamer = simpledialog.askstring(title='Play a custom stream',
                        prompt='Play a stream without adding it to your list',
                        parent=root
                        )
    if streamer is None or len(streamer) == 0:
        return
    else:
        update = subprocess.run(['wtwitch', 'w', streamer],
                        capture_output=True,
                        text=True
                        )

def refresh_main_quiet():
    '''Refresh the main panel without running wtwitch c to avoid unnecessary
    Twitch API calls.
    '''
    global streamer_status
    try:
        streamer_status = twitchapi.extract_streamer_status()
    except:
        error_dialog()
    twitchapi.extract_streamer_status()
    main_frame.pack_forget()
    main_frame.destroy()
    draw_main()

def refresh_main():
    '''Runs wtwitch c and then rebuilds the main panel.
    '''
    twitchapi.check_status()
    global streamer_status
    try:
        streamer_status = twitchapi.extract_streamer_status()
    except:
        error_dialog()
    main_frame.pack_forget()
    main_frame.destroy()
    draw_main()

def mouse_scroll(event):
    meta_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def draw_main():
    '''The main window. Calls streamer_buttons() twice, to draw buttons for
    online and offline streamers.
    '''
    # frame-canvas-frame to attach a scrollbar:
    meta_frame = ttk.Frame(root)
    meta_frame.grid(column='0', row='0', sticky='nsew')
    meta_canvas = tk.Canvas(meta_frame, highlightthickness='0')
    scrollbar = ttk.Scrollbar(meta_frame,
                        orient="vertical", command=meta_canvas.yview)
    meta_canvas.configure(yscrollcommand=scrollbar.set)
    global main_frame
    main_frame = ttk.Frame(meta_canvas)
    main_frame.grid(column=0, row=0, sticky='nesw')
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)
    main_frame.bind("<Configure>", lambda e:
                        meta_canvas.configure(
                        scrollregion=meta_canvas.bbox("all"))
                        )
    # Draw main content:
    streamer_buttons(main_frame)
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
    new_player = simpledialog.askstring(title='Player',
                        prompt='Enter your media player:',
                        parent=settings_window,
                        initialvalue=twitchapi.check_config()[0])
    if new_player is None or len(new_player) == 0:
        return
    else:
        twitchapi.adjust_config('player', new_player)

def custom_quality():
    '''Opens a dialog to set a custom stream quality.
    '''
    new_quality = simpledialog.askstring(title='Quality',
                        prompt= '\n Options: 1080p60, 720p60, 720p, 480p, \n'
                                ' 360p, 160p, best, worst, and audio_only \n'
                                '\n'
                                ' Specify fallbacks separated by a comma: \n'
                                ' E.g. "720p,480p,worst" \n',
                        initialvalue=twitchapi.check_config()[1],
                        parent=settings_window)
    if new_quality is None or len(new_quality) == 0:
        return
    else:
        twitchapi.adjust_config('quality', new_quality)


def settings_dialog():
    '''Opens a toplevel window with four settings options.
    '''
    global selected_player
    selected_player = tk.StringVar()
    if twitchapi.check_config()[0] in ['mpv', 'vlc']:
        selected_player.set(twitchapi.check_config()[0])
    else:
        selected_player.set('custom')
    global selected_quality
    selected_quality = tk.StringVar()
    if twitchapi.check_config()[1] in ['best', '720p,720p60,480p,best', '480p,worst']:
        selected_quality.set(twitchapi.check_config()[1])
    else:
        selected_quality.set('custom')
    global settings_window
    settings_window = tk.Toplevel(master=root)
    settings_window.title('Settings')
    settings_window.transient(root)
    settings_window.grab_set()
    meta_frame = ttk.Frame(settings_window)
    meta_frame.pack(expand=True, fill='both', ipadx=10, ipady=10)
    top_f = ttk.Frame(meta_frame)
    top_f.pack()
    qual_f = ttk.Labelframe(top_f, text='Stream quality')
    qual_f.pack(side='left', anchor='nw', padx=5, pady=5)
    high_qual = ttk.Radiobutton(qual_f, text='High',
                value='best', variable=selected_quality,
                command=lambda: twitchapi.adjust_config('quality', 'best')
                )
    high_qual.pack(expand=True, fill='both')
    mid_qual = ttk.Radiobutton(qual_f, text='Medium',
                value='720p,720p60,480p,best', variable=selected_quality,
                command=lambda: twitchapi.adjust_config('quality', '720p,720p60,480p,best')
                )
    mid_qual.pack(expand=True, fill='both')
    low_qual = ttk.Radiobutton(qual_f, text='Low',
                value='480p,worst', variable=selected_quality,
                command=lambda: twitchapi.adjust_config('quality', '480p, worst')
                )
    low_qual.pack(expand=True, fill='both')
    custom_qual = ttk.Radiobutton(qual_f, text='Custom',
                value='custom', variable=selected_quality,
                command=lambda: custom_quality())
    custom_qual.pack(expand=True, fill='both')
    play_f = ttk.Labelframe(top_f, text='Choose player')
    play_f.pack(side='right', anchor='ne', padx=5, pady=5)
    pick_mpv = ttk.Radiobutton(play_f, text='mpv',
                value='mpv', variable=selected_player,
                command=lambda: twitchapi.adjust_config('player', 'mpv')
                )
    pick_mpv.pack(expand=True, fill='both')
    pick_vlc = ttk.Radiobutton(play_f, text='VLC',
                value='vlc', variable=selected_player,
                command=lambda: twitchapi.adjust_config('player', 'vlc')
                )
    pick_vlc.pack(expand=True, fill='both')
    pick_custom = ttk.Radiobutton(play_f, text='Custom',
                value='custom', variable=selected_player,
                command=lambda: custom_player())
    pick_custom.pack(expand=True, fill='both')
    bottom_f = ttk.Frame(meta_frame)
    bottom_f.pack()
    global selected_theme
    style = ttk.Style()
    selected_theme = tk.StringVar()
    theme_f = ttk.LabelFrame(bottom_f, text='Themes')
    theme_f.pack(anchor='nw', side='left', padx=5, pady=5)
    for theme_name in ttk.Style.theme_names(style):
        pick_theme = ttk.Radiobutton(theme_f,
                text=theme_name,
                value=theme_name,
                variable=selected_theme,
                command=lambda t=theme_name: style.theme_use(t)
                )
        pick_theme.pack(expand=True, fill='both')
    scale_f = ttk.Labelframe(bottom_f, text='Window scale')
    scale_f.pack(side='left', anchor='nw', padx=5, pady=5)
    color_f = ttk.Labelframe(bottom_f, text='Window color:')
    color_f.pack(side='right', anchor='ne', padx=5, pady=5)

def menu_bar():
    '''The menu bar of the root window.
    '''
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    menubar.add_command(label='Refresh', font=bold_font,
            command=lambda: refresh_main())
    menubar.add_command(label='Follow', font=normal_font,
            command=lambda: follow_dialog())
    menubar.add_command(label='Play', font=normal_font,
            command=lambda: play_dialog())
    menubar.add_command(label='Settings', font=normal_font,
            command=lambda: settings_dialog())

def window_size():
    """Sets the default window length, depending on the number of streamers in
    the follow list. Fixed between 360 and 550 px. Width fixed at 285 px.
    """
    min_height = 360
    max_height = 550
    variable_height = len(streamer_status[0])*28+len(streamer_status[1])*28+100
    if variable_height > max_height:
        window_height = str(max_height)
    elif variable_height < min_height:
        window_height = str(min_height)
    else:
        window_height = str(variable_height)
    return f"285x{window_height}"

def toggle_settings():
    """Checks if wtwitch prints offline streamers and color output. Latter is
    needed to filter wtwitch output with regex.
    """
    if twitchapi.check_config()[2] == 'false':
        twitchapi.adjust_config('colors', 'true')
    if twitchapi.check_config()[3] == 'false':
        twitchapi.adjust_config('printOfflineSubscriptions', 'true')

# Make sure that colors in the terminal output are activated:
toggle_settings()
# Check the online/offline status once before window initialization:
twitchapi.check_status()
try:
    streamer_status = twitchapi.extract_streamer_status()
except:
    error_dialog()

# Create the main window
root = tk.Tk(className='GUI for wtwitch')
root.title("GUI for wtwitch")
root.geometry(window_size())
root.resizable(False, True)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Fonts:
normal_font = ('Cantarell', '12')
bold_font = ('Cantarell', '12', 'bold')
big_font = ('Cantarell', '13', 'bold')
bigbold_font = ('Cantarell', '13', 'bold')

# Import icons:
unfollow_icon = tk.PhotoImage(file=encoded_images.unfollow_icon)
vod_icon = tk.PhotoImage(file=encoded_images.vod_icon)
streaming_icon = tk.PhotoImage(file=encoded_images.streaming_icon)
offline_icon = tk.PhotoImage(file=encoded_images.offline_icon)
play_icon = tk.PhotoImage(file=encoded_images.play_icon)
close_icon = tk.PhotoImage(file=encoded_images.close_icon)

app_icon = tk.PhotoImage(file=encoded_images.app_icon)
root.iconphoto(False, app_icon)

# Remove icon temp files:
os.remove(encoded_images.unfollow_icon)
os.remove(encoded_images.vod_icon)
os.remove(encoded_images.streaming_icon)
os.remove(encoded_images.offline_icon)
os.remove(encoded_images.play_icon)
os.remove(encoded_images.close_icon)
os.remove(encoded_images.app_icon)

menu_bar()
draw_main()
root.mainloop()