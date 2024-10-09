#!/usr/bin/env python

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
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
    vw_frame.grid(column=0, row=1, sticky='nsew')
    vw_frame.columnconfigure(0, weight=1)
    vw_frame.rowconfigure(0, weight=1)
    met_frame = ttk.Frame(vw_frame)
    met_frame.grid(column=0, row=1, sticky='nsew')
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
                        [twitchapi.start_vod(s, v)]
                        )
        watch_button.grid(column=0, row=vod_number, sticky='nesw')
        timestamp_button = tk.Button(vod_frame, text=f"{timestamp} ({length})",
                        command=lambda ts=timestamp, t=title, p=root:
                        messagebox.showinfo("VOD", ts, detail=t, parent=p),
                        font=small_font,
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

def streamer_buttons():
    online_streamers = streamer_status[0]
    offline_streamers = streamer_status[1]
    count_rows = 0
    for package in online_streamers:
        show_info_status[count_rows] = False
        watch_button = tk.Button(main_frame,
                        image=streaming_icon,
                        relief='flat',
                        command=lambda s=package[0]:
                        [twitchapi.start_stream(s)]
                        )
        watch_button.grid(column=0, row=count_rows, sticky='nsew', ipadx=4)
        if current_info_setting == 'all' or current_info_setting == 'online':
            watch_button.grid_configure(rowspan=2)
            info_button = tk.Button(main_frame,
                            text=package[1],
                            anchor='w',
                            font=cantarell_13_bold,
                            relief='flat',
                            state='disabled',
                            disabledforeground='#000000'
                            )
            online_info(count_rows, package[1], package[2],
                        package[3], package[4]
                        )
        else:
            info_button = tk.Button(main_frame,
                            text=package[1],
                            anchor='w',
                            font=cantarell_13_bold,
                            relief='flat',
                            command=lambda c=count_rows, s=package[1],
                                        cat=package[2], t=package[3],
                                        v=package[4]:
                                        online_info(c, s, cat, t, v)
                            )
        info_button.grid(column=1, row=count_rows, sticky='nsew')
        unfollow_b = tk.Button(main_frame,
                        image=unfollow_icon,
                        relief='flat',
                        command=lambda s=package[0]:
                        [unfollow_dialog(s)]
                        )
        unfollow_b.grid(column=2, row=count_rows, sticky='nsew', ipadx=4)
        vod_b = tk.Button(main_frame,
                        image=vod_icon,
                        relief='flat',
                        command=lambda s=package[0]:
                        vod_panel(s)
                        )
        vod_b.grid(column=3, row=count_rows, sticky='nsew', ipadx=8)
        ttk.Separator(main_frame).grid(row=count_rows+2,
                                        columnspan=5,
                                        sticky='ew'
                                        )
        count_rows += 3
    for streamer in offline_streamers:
        show_info_status[count_rows] = False
        watch_button = tk.Label(main_frame,
                        image=offline_icon,
                        relief='flat'
                        )
        watch_button.grid(column=0, row=count_rows, sticky='nsew', ipadx=4)
        if current_info_setting == 'all':
            watch_button.grid_configure(rowspan=2)
            info_button = tk.Button(main_frame,
                            text=streamer,
                            anchor='w',
                            font=cantarell_13_bold,
                            relief='flat',
                            state='disabled',
                            disabledforeground='#474747'
                            )
            offline_info(count_rows, streamer)
        else:
            info_button = tk.Button(main_frame,
                            text=streamer,
                            anchor='w',
                            font=cantarell_13_bold,
                            fg='#474747',
                            relief='flat',
                            compound='left',
                            command= lambda s=streamer, c=count_rows:
                                    offline_info(c, s)
                            )
        info_button.grid(column=1, row=count_rows, sticky='nsew')
        unfollow_b = tk.Button(main_frame,
                        image=unfollow_icon,
                        relief='flat',
                        command=lambda s=streamer:
                        [unfollow_dialog(s)]
                        )
        unfollow_b.grid(column=2, row=count_rows, sticky='nsew', ipadx=4)
        vod_b = tk.Button(main_frame,
                        image=vod_icon,
                        relief='flat',
                        command=lambda s=streamer:
                        vod_panel(s)
                        )
        vod_b.grid(column=3, row=count_rows, sticky='nsew', ipadx=8)
        if count_rows != (len(online_streamers)+len(offline_streamers))*3-3:
            ttk.Separator(main_frame).grid(row=count_rows+2,
                                            columnspan=5,
                                            sticky='ew'
                                            )
        count_rows += 3

def online_info(c, streamer, category, title, viewercount):
    if not show_info_status[c]:
        info_content[c] = tk.Label(main_frame,
                                    text=f'Title: {title}\n'
                                    f'Category: {category}\n'
                                    f'Viewer count: {viewercount}',
                                    justify='left',
                                    anchor='w'
                                    )
        info_content[c].grid(row=c+1, column=1, columnspan=4, sticky='w', padx=10)
        show_info_status[c] = True
    else:
        info_content[c].grid_remove()
        show_info_status[c] = False

def offline_info(c, streamer):
    if not show_info_status[c]:
        info_content[c] = tk.Label(main_frame,
                                    text=f'Last seen: '
                                    f'{twitchapi.last_seen(streamer)}',
                                    justify='left',
                                    anchor='w',
                                    fg='#474747'
                                    )
        info_content[c].grid(row=c+1, column=1, columnspan=4, sticky='w')
        show_info_status[c] = True
    else:
        info_content[c].grid_remove()
        show_info_status[c] = False

def error_dialog(e):
    messagebox.showerror(title='Error',
                        message=f'{e}\n\n Check your internet connection!',
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
                                    prompt='Play a stream without adding it\n'
                                    'to your follow list',
                                    parent=root
                                    )
    if streamer is None or len(streamer) == 0:
        return
    else:
        update = twitchapi.start_stream(streamer)

def refresh_main_quiet():
    '''Refresh the main panel without running wtwitch c to avoid unnecessary
    Twitch API calls.
    '''
    global streamer_status
    try:
        streamer_status = twitchapi.extract_streamer_status()
    except Exception as e:
        error_dialog(e)
    twitchapi.extract_streamer_status()
    for widget in main_frame.winfo_children():
        widget.destroy()
    streamer_buttons()

def refresh_main():
    '''Runs wtwitch c and then rebuilds the main panel.
    '''
    twitchapi.check_status()
    global streamer_status
    try:
        streamer_status = twitchapi.extract_streamer_status()
    except Exception as e:
        error_dialog(e)
    for widget in main_frame.winfo_children():
        widget.destroy()
    streamer_buttons()

def resize_meta_canvas(e):
    meta_canvas.itemconfig(meta_canvas_window, width=e.width)

def mouse_scroll(event):
    meta_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def draw_main():
    '''The main window. Calls streamer_buttons() twice, to draw buttons for
    online and offline streamers.
    '''
    # frame-canvas-frame to attach a scrollbar:
    meta_frame = ttk.Frame(root)
    meta_frame.grid(row=0, column=0, sticky='nsew')
    meta_frame.columnconfigure(0, weight=1)
    meta_frame.rowconfigure(0, weight=1)
    global meta_canvas
    meta_canvas = tk.Canvas(meta_frame, highlightthickness='0')
    meta_canvas.grid(row=0, column=0, sticky="nsew")
    meta_canvas.columnconfigure(0, weight=1)
    meta_canvas.rowconfigure(0, weight=1)
    scrollbar = ttk.Scrollbar(meta_frame,
                        orient="vertical", command=meta_canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    meta_canvas.configure(yscrollcommand=scrollbar.set)
    global main_frame
    main_frame = ttk.Frame(meta_canvas)
    main_frame.grid(row=0, column=0, sticky='nsew')
    main_frame.columnconfigure(1, weight=1)
    main_frame.bind("<Configure>", lambda e:
                        meta_canvas.configure(
                        scrollregion=meta_canvas.bbox("all")
                        )
                    )
    global meta_canvas_window
    meta_canvas_window = meta_canvas.create_window((0, 0), window=main_frame, anchor="nw")
    meta_canvas.bind("<Configure>", resize_meta_canvas)
    meta_canvas.bind("<MouseWheel>", mouse_scroll)
    # Draw main content:
    streamer_buttons()

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

def change_info_preset(value):
    twitchapi.change_settings_file('show_info_preset', value)
    global current_info_setting
    global preset_info_setting
    preset_info_setting = twitchapi.get_setting('show_info_preset')
    if preset_info_setting == current_info_setting or current_info_setting == 'no':
        return
    else:
        twitchapi.change_settings_file('show_info', value)
        current_info_setting = preset_info_setting
        refresh_main_quiet()

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
    global expand_info_setting
    expand_info_setting = tk.StringVar()
    expand_info_setting.set(preset_info_setting)
    info_f = ttk.LabelFrame(bottom_f, text='Expand info')
    info_f.pack(anchor='nw', side='left', padx=5, pady=5)
    all_info = ttk.Radiobutton(info_f, text='All',
                value='all', variable=expand_info_setting,
                command=lambda: [change_info_preset('all')])
    all_info.pack(expand=True, fill='both')
    only_online_info = ttk.Radiobutton(info_f, text='Only online',
                value='online', variable=expand_info_setting,
                command=lambda: [change_info_preset('online')])
    only_online_info.pack(expand=True, fill='both')
    global selected_theme
    style = ttk.Style()
    selected_theme = tk.StringVar()
    theme_f = ttk.LabelFrame(bottom_f, text='Themes')
    theme_f.pack(anchor='nw', side='right', padx=5, pady=5)
    for theme_name in ttk.Style.theme_names(style):
        pick_theme = ttk.Radiobutton(theme_f,
                text=theme_name,
                value=theme_name,
                variable=selected_theme,
                command=lambda t=theme_name: style.theme_use(t)
                )
        pick_theme.pack(expand=True, fill='both')

def set_quick_toggle_icon():
    global current_info_setting
    global current_quick_toggle_icon
    if current_info_setting == 'no':
        current_quick_toggle_icon = expand_icon
    else:
        current_quick_toggle_icon = collapse_icon
    return current_quick_toggle_icon

def info_quick_toggle():
    global current_info_setting
    if current_info_setting == 'no':
        twitchapi.change_settings_file('show_info', preset_info_setting)
    else:
        twitchapi.change_settings_file('show_info', 'no')
    current_info_setting = twitchapi.get_setting('show_info')
    refresh_main_quiet()

def menu_bar():
    '''The menu bar of the root window.
    '''
    global current_quick_toggle_icon
    current_quick_toggle_icon = set_quick_toggle_icon()
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    menubar.add_command(label='Refresh', font=cantarell_12_bold,
                        command=lambda: refresh_main())
    menubar.add_command(label='Follow', font=cantarell_12,
                        command=lambda: follow_dialog())
    menubar.add_command(label='Play', font=cantarell_12,
                        command=lambda: play_dialog())
    menubar.add_command(image=settings_icon, font=cantarell_12,
                        command=lambda: settings_dialog())
    menubar.add_command(image=current_quick_toggle_icon, font=cantarell_12,
                        command=lambda: [info_quick_toggle(),
                                        set_quick_toggle_icon(),
                                        menubar.entryconfigure(5,
                                        image=current_quick_toggle_icon)
                                        ]
                                    )

def save_window_size(event):
    twitchapi.change_settings_file('window_size', root.wm_geometry())

def initiate_window_dimensions():
    """Sets the default window length, depending on the number of streamers in
    the follow list. Fixed between 360 and 650 px.
    """
    try:
        return twitchapi.get_setting('window_size')
    except:
        min_height = 360
        max_height = 650
        variable_height = len(streamer_status[0])*28+len(streamer_status[1])*28+100
        if variable_height > max_height:
            window_height = str(max_height)
        elif variable_height < min_height:
            window_height = str(min_height)
        else:
            window_height = str(variable_height)
        return f'330x{window_height}'

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
except Exception as e:
    error_dialog(e)
# Create a gwt-specific settings file:
twitchapi.create_settings_file()

# Create the main window
root = tk.Tk(className='GUI for wtwitch')
root.title("GUI for wtwitch")
root.geometry(initiate_window_dimensions())
root.minsize(285, 360)
root.bind("<Destroy>", save_window_size)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Fonts:
small_font = ('', 10)
cantarell_12 = ('Cantarell', 12)
cantarell_12_bold = ('Cantarell', 12, 'bold')
cantarell_13_bold = ('Cantarell', 13, 'bold')

# Import icons:
icon_files = twitchapi.icon_paths()
unfollow_icon = tk.PhotoImage(file=icon_files['unfollow_icon'])
vod_icon = tk.PhotoImage(file=icon_files['vod_icon'])
streaming_icon = tk.PhotoImage(file=icon_files['streaming_icon'])
offline_icon = tk.PhotoImage(file=icon_files['offline_icon'])
play_icon = tk.PhotoImage(file=icon_files['play_icon'])
close_icon = tk.PhotoImage(file=icon_files['close_icon'])
settings_icon = tk.PhotoImage(file=icon_files['settings_icon'])

expand_icon = tk.PhotoImage(file=icon_files['expand_icon'])
collapse_icon = tk.PhotoImage(file=icon_files['collapse_icon'])

app_icon = tk.PhotoImage(file=icon_files['app_icon'])
root.iconphoto(False, app_icon)

# Variables to collect stream info
# and settings value to show info for all streamers:
show_info_status = {}
info_content = {}
preset_info_setting = tk.StringVar()
preset_info_setting = twitchapi.get_setting('show_info_preset')
current_info_setting = twitchapi.get_setting('show_info')

menu_bar()
draw_main()
root.mainloop()