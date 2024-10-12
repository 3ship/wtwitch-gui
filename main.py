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
    global current_vod_panel
    current_vod_panel = streamer
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
    global vw_frame
    vw_frame = default_frame(root)
    vw_frame.grid(column=0, row=1, sticky='nsew')
    vw_frame.columnconfigure(0, weight=1)
    vw_frame.rowconfigure(0, weight=1)
    met_frame = default_frame(vw_frame)
    met_frame.grid(column=0, row=0, sticky='nsew')
    met_frame.columnconfigure(0, weight=1)
    met_frame.rowconfigure(0, weight=1)
    global vw_canvas
    vw_canvas = default_canvas(met_frame)
    vw_scrollbar = ttk.Scrollbar(met_frame,orient="vertical",
                        command=vw_canvas.yview
                        )
    vw_canvas.configure(yscrollcommand=vw_scrollbar.set)
    global vod_frame
    vod_frame = default_frame(met_frame)
    vod_frame.grid(column=0, row=0, sticky='nsew')
    vod_frame.columnconfigure(1, weight=1)
    vod_frame.rowconfigure(0, weight=1)
    vod_frame.bind("<Configure>", lambda e:
                        vw_canvas.configure(
                        scrollregion=vw_canvas.bbox("all"))
                        )
    # Draw the VOD grid:
    close_button = default_button(
                        vod_frame,
                        image=close_icon,
                        command=lambda: close_vod_panel()
                        )
    close_button.grid(column=0, row=0, sticky='nw', ipady=12, ipadx=12)
    vod_label = default_label(vod_frame,
                        text=f'{streamer}\'s VODs'
                        )
    vod_label.grid(column=1, row=0)
    separator = default_separator(vod_frame)
    separator[0].grid(row=1)
    separator[1].grid(row=2)
    vod_number = 1
    count_vod_rows = 3
    for timestamp, title, length in zip(vods[0], vods[1], vods[2]):
        vod_info_status[count_vod_rows] = False
        watch_button = default_button(vod_frame,
                        image=play_icon,
                        height='24', width='24',
                        command=lambda s=streamer, v=vod_number:
                        [twitchapi.start_vod(s, v)]
                        )
        watch_button.grid(column=0, row=count_vod_rows, sticky='nesw')
        if current_info_setting == 'all' or current_info_setting == 'online':
            timestamp_button = default_button(vod_frame,
                            text=f"{timestamp} {length}",
                            anchor='w',
                            state='disabled',
                            font=small_font,
                            )
            vod_info(count_vod_rows, title)
        else:
            timestamp_button = default_button(vod_frame,
                        text=f"{timestamp} {length}",
                        command=lambda c=count_vod_rows, t=title:
                        vod_info(c, t),
                        font=small_font,
                        anchor='w'
                        )
        timestamp_button.grid(column=1, row=count_vod_rows, sticky='nesw')
        if vod_number != len(vods[0]):
            separator = default_separator(vod_frame)
            separator[0].grid(row=count_vod_rows+2)
            separator[1].grid(row=count_vod_rows+3)
        vod_number += 1
        count_vod_rows += 4
    # Finish the scrollbar
    global vw_canvas_window
    vw_canvas_window = vw_canvas.create_window(
                                            (0, 0),
                                            window=vod_frame,
                                            anchor="nw"
                                            )
    vw_canvas.grid(row=0, column=0, sticky="nsew")
    vw_scrollbar.grid(row=0, column=1, sticky="ns")
    vw_canvas.bind("<Configure>", resize_canvas)

def vod_info(cr, title):
    if not vod_info_status[cr]:
        vod_info_content[cr] = default_label(vod_frame,
                                    text=f'{title}',
                                    justify='left',
                                    anchor='w',
                                    )
        vod_info_content[cr].grid(
                                row=cr+1,
                                column=0,
                                columnspan=3,
                                sticky='w',
                                padx=10
                                )
        vod_info_status[cr] = True
    else:
        vod_info_content[cr].grid_remove()
        vod_info_status[cr] = False

def refresh_vod_panel(streamer):
    for widget in vod_frame.winfo_children():
        widget.destroy()
    vod_panel(streamer)

def close_vod_panel():
    vw_frame.forget()
    vw_frame.destroy()
    main_frame.destroy()
    draw_main()

def streamer_buttons():
    online_streamers = streamer_status[0]
    offline_streamers = streamer_status[1]
    count_rows = 0
    for package in online_streamers:
        stream_info_status[count_rows] = False
        watch_button = default_button(main_frame,
                        image=streaming_icon,
                        command=lambda s=package[0]:
                        [twitchapi.start_stream(s)]
                        )
        watch_button.grid(
                        column=0,
                        row=count_rows,
                        sticky='nsew',
                        ipadx=4,
                        ipady=8
                        )
        if current_info_setting == 'all' or current_info_setting == 'online':
            watch_button.grid_configure(rowspan=2)
            info_button = default_button(main_frame,
                            text=package[1],
                            anchor='w',
                            font=cantarell_13_bold,
                            state='disabled',
                            )
            online_info(count_rows, package[1], package[2],
                        package[3], package[4]
                        )
        else:
            info_button = default_button(main_frame,
                            text=package[1],
                            anchor='w',
                            font=cantarell_13_bold,
                            command=lambda c=count_rows, s=package[1],
                                        cat=package[2], t=package[3],
                                        v=package[4]:
                                        online_info(c, s, cat, t, v)
                            )
        info_button.grid(column=1, row=count_rows, sticky='nsew')
        unfollow_b = default_button(main_frame,
                        image=unfollow_icon,
                        command=lambda s=package[0]:
                        [unfollow_dialog(s)]
                        )
        unfollow_b.grid(column=2, row=count_rows, sticky='nsew', ipadx=4)
        vod_b = default_button(main_frame,
                        image=vod_icon,
                        command=lambda s=package[0]:
                        vod_panel(s)
                        )
        vod_b.grid(column=3, row=count_rows, sticky='nsew', ipadx=8)
        separator = default_separator(main_frame)
        separator[0].grid(row=count_rows+2)
        separator[1].grid(row=count_rows+3)
        count_rows += 4
    for streamer in offline_streamers:
        stream_info_status[count_rows] = False
        watch_button = default_label(main_frame,
                        image=offline_icon,
                        )
        watch_button.grid(
                        column=0,
                        row=count_rows,
                        sticky='nsew',
                        ipadx=4,
                        ipady=6
                        )
        if current_info_setting == 'all':
            watch_button.grid_configure(rowspan=2)
            info_button = default_button(main_frame, 'offline',
                            text=streamer,
                            anchor='w',
                            font=cantarell_13_bold,
                            state='disabled',
                            )
            offline_info(count_rows, streamer)
        else:
            info_button = default_button(main_frame, 'offline',
                            text=streamer,
                            anchor='w',
                            font=cantarell_13_bold,
                            compound='left',
                            command= lambda s=streamer, c=count_rows:
                                    offline_info(c, s)
                            )
        info_button.grid(column=1, row=count_rows, sticky='nsew')
        unfollow_b = default_button(main_frame,
                        image=unfollow_icon,
                        command=lambda s=streamer:
                        [unfollow_dialog(s)]
                        )
        unfollow_b.grid(column=2, row=count_rows, sticky='nsew', ipadx=4)
        vod_b = default_button(main_frame,
                        image=vod_icon,
                        command=lambda s=streamer:
                        vod_panel(s)
                        )
        vod_b.grid(column=3, row=count_rows, sticky='nsew', ipadx=8)
        if count_rows != (len(online_streamers)+len(offline_streamers))*4-4:
            sep = default_separator(main_frame)
            sep[0].grid(row=count_rows+2)
            sep[1].grid(row=count_rows+3)
        count_rows += 4

def online_info(c, streamer, category, title, viewercount):
    if not stream_info_status[c]:
        stream_info_content[c] = default_label(main_frame,
                                    text=f'Title: {title}\n'
                                    f'Category: {category}\n'
                                    f'Viewer count: {viewercount}',
                                    justify='left',
                                    anchor='w',
                                    )
        stream_info_content[c].grid(row=c+1,
                                    column=1,
                                    columnspan=4,
                                    sticky='w',
                                    padx=10
                                    )
        stream_info_status[c] = True
    else:
        stream_info_content[c].grid_remove()
        stream_info_status[c] = False

def offline_info(c, streamer):
    if not stream_info_status[c]:
        stream_info_content[c] = default_label(main_frame, 'offline',
                                    text=f'Last seen: '
                                    f'{twitchapi.last_seen(streamer)}',
                                    justify='left',
                                    anchor='w',
                                    )
        stream_info_content[c].grid(row=c+1,
                                    column=1,
                                    columnspan=4,
                                    sticky='w',
                                    padx=10
                                    )
        stream_info_status[c] = True
    else:
        stream_info_content[c].grid_remove()
        stream_info_status[c] = False

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
    try:
        refresh_vod_panel(current_vod_panel)
    except:
        pass

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

def resize_canvas(e):
    meta_canvas.itemconfig(meta_canvas_window, width=e.width)
    try:
        vw_canvas.itemconfig(vw_canvas_window, width=e.width)
    except:
        pass

def draw_main():
    '''The main window. Calls streamer_buttons() twice, to draw buttons for
    online and offline streamers.
    '''
    # frame-canvas-frame to attach a scrollbar:
    meta_frame = default_frame(root)
    meta_frame.grid(row=1, column=0, sticky='nsew')
    meta_frame.columnconfigure(0, weight=1)
    meta_frame.rowconfigure(0, weight=1)
    global meta_canvas
    meta_canvas = default_canvas(meta_frame)
    meta_canvas.grid(row=0, column=0, sticky="nsew")
    meta_canvas.columnconfigure(0, weight=1)
    meta_canvas.rowconfigure(0, weight=1)
    scrollbar = ttk.Scrollbar(meta_frame,
                        orient="vertical", command=meta_canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    meta_canvas.configure(yscrollcommand=scrollbar.set)
    global main_frame
    main_frame = default_frame(meta_canvas)
    main_frame.grid(row=0, column=0, sticky='nsew')
    main_frame.columnconfigure(1, weight=1)
    global meta_canvas_window
    meta_canvas_window = meta_canvas.create_window(
                                                (0, 0),
                                                window=main_frame,
                                                anchor="nw"
                                                )
    meta_canvas.bind("<Configure>", resize_canvas)
    # Draw main content:
    streamer_buttons()
    main_frame.bind("<Configure>", lambda event:
                                    meta_canvas.configure(
                                        scrollregion=meta_canvas.bbox("all")))

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
    cis = current_info_setting
    if preset_info_setting == cis or cis == 'no':
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
    if twitchapi.check_config()[1] in [
                                        'best',
                                        '720p,720p60,480p,best',
                                        '480p,worst'
                                        ]:
        selected_quality.set(twitchapi.check_config()[1])
    else:
        selected_quality.set('custom')
    global settings_window
    settings_window = tk.Toplevel(master=root)
    settings_window.title('Settings')
    settings_window.transient(root)
    settings_window.grab_set()
    meta_frame = default_frame(settings_window)
    meta_frame.pack(expand=True, fill='both', ipadx=10, ipady=10)
    top_f = default_frame(meta_frame)
    top_f.pack()
    qual_f = default_frame(top_f)
    qual_f.pack(side='left', anchor='nw', padx=12, pady=12)
    default_label(qual_f, text='Video quality:').pack()
    high_qual = default_radiobutton(qual_f,
                text='High',
                value='best',
                variable=selected_quality,
                command=lambda: twitchapi.adjust_config(
                                                'quality',
                                                'best'
                                                )
                )
    high_qual.pack(expand=True, fill='both')
    mid_qual = default_radiobutton(qual_f,
                text='Medium',
                value='720p,720p60,480p,best',
                variable=selected_quality,
                command=lambda: twitchapi.adjust_config(
                                                'quality',
                                                '720p,720p60,480p,best'
                                                )
                )
    mid_qual.pack(expand=True, fill='both')
    low_qual = default_radiobutton(qual_f,
                text='Low',
                value='480p,worst',
                variable=selected_quality,
                command=lambda: twitchapi.adjust_config(
                                                'quality',
                                                '480p,worst'
                                                )
                )
    low_qual.pack(expand=True, fill='both')
    custom_qual = default_radiobutton(qual_f,
                text='Custom',
                value='custom',
                variable=selected_quality,
                command=lambda: custom_quality())
    custom_qual.pack(expand=True, fill='both')
    play_f = default_frame(top_f)
    play_f.pack(side='right', anchor='ne', padx=12, pady=12)
    default_label(play_f, text='Media player:').pack()
    pick_mpv = default_radiobutton(play_f,
                text='mpv',
                value='mpv',
                variable=selected_player,
                command=lambda: twitchapi.adjust_config(
                                                'player',
                                                'mpv'
                                                )
                )
    pick_mpv.pack(expand=True, fill='both')
    pick_vlc = default_radiobutton(play_f,
                text='VLC',
                value='vlc',
                variable=selected_player,
                command=lambda: twitchapi.adjust_config(
                                                'player',
                                                'vlc'
                                                )
                )
    pick_vlc.pack(expand=True, fill='both')
    pick_custom = default_radiobutton(play_f,
                text='Custom',
                value='custom',
                variable=selected_player,
                command=lambda: custom_player()
                )
    pick_custom.pack(expand=True, fill='both')
    bottom_f = default_frame(meta_frame)
    bottom_f.pack()
    global expand_info_setting
    expand_info_setting = tk.StringVar()
    expand_info_setting.set(preset_info_setting)
    info_f = default_frame(bottom_f, borderwidth=1)
    info_f.pack(anchor='nw', side='left', padx=12, pady=12)
    default_label(info_f, text='Expand info:').pack()
    all_info = default_radiobutton(info_f,
                text='All',
                value='all',
                variable=expand_info_setting,
                command=lambda: [change_info_preset('all')]
                )
    all_info.pack(expand=True, fill='both')
    only_online_info = default_radiobutton(info_f,
                text='Only online',
                value='online',
                variable=expand_info_setting,
                command=lambda: [change_info_preset('online')]
                )
    only_online_info.pack(expand=True, fill='both')

def set_quick_toggle_icon(n):
    global current_info_setting
    global current_quick_toggle_icon
    global expand_b
    if current_info_setting == 'no':
        current_quick_toggle_icon = expand_icon
    else:
        current_quick_toggle_icon = collapse_icon
    if n == 1:
        expand_b.config(image=current_quick_toggle_icon)
    return current_quick_toggle_icon

def info_quick_toggle():
    global current_info_setting
    if current_info_setting == 'no':
        twitchapi.change_settings_file('show_info', preset_info_setting)
    else:
        twitchapi.change_settings_file('show_info', 'no')
    current_info_setting = twitchapi.get_setting('show_info')
    refresh_main_quiet()

def custom_menu_bar():
    global current_quick_toggle_icon
    current_quick_toggle_icon = set_quick_toggle_icon(0)
    menu_frame = default_frame(root)
    menu_frame.grid(row=0, column=0, sticky='nesw')
    menu_frame.columnconfigure(2, weight=1)
    refresh_b = default_button(menu_frame,
                    text='Refresh',
                    font=cantarell_12_bold,
                    command=lambda: refresh_main()
                    )
    refresh_b.grid(row=0, column=0)
    follow_b = default_button(menu_frame,
                    text='Follow',
                    font=cantarell_12,
                    command=lambda: follow_dialog()
                    )
    follow_b.grid(row=0, column=1)
    play_b = default_button(menu_frame,
                    text='Play',
                    font=cantarell_12,
                    command=lambda: play_dialog()
                    )
    play_b.grid(row=0, column=2, sticky='w')
    settings_b = default_button(menu_frame,
                    image=settings_icon,
                    font=cantarell_12,
                    command=lambda: settings_dialog()
                    )
    settings_b.grid(row=0, column=3, sticky='e')
    global expand_b
    expand_b = default_button(menu_frame,
                    image=current_quick_toggle_icon,
                    font=cantarell_12
                    )
    expand_b.grid(row=0, column=4, sticky='e')
    expand_b.configure(command=lambda: [
                                        info_quick_toggle(),
                                        set_quick_toggle_icon(1)
                                        ]
                        )
    sep = default_separator(menu_frame)

def default_radiobutton(master, *args, **kwargs):
    if is_gnome_darkmode:
        info_font = '#BDBDBD'
        button = tk.Radiobutton(
            master,
            bg='#333333',
            fg=info_font,
            activebackground='#3F3F3F',
            selectcolor='#242424',
            activeforeground=info_font,
            disabledforeground=info_font,
            highlightthickness=0,
            relief='flat',
            anchor='w',
            border=0,
            **kwargs
        )
    else:
        info_font = '#000000'
        button = tk.Radiobutton(
            master,
            highlightthickness=0,
            fg=info_font,
            activeforeground=info_font,
            disabledforeground=info_font,
            relief='flat',
            anchor='w',
            border=0,
            **kwargs
        )
    return button

def default_separator(master, **kwargs):
    if is_gnome_darkmode:
        sep1 = tk.Frame(
            master,
            bg='#090909',
            height=1,
            border=0,
            **kwargs
        )
        sep2 = tk.Frame(
            master,
            bg='#545454',
            height=1,
            border=0,
            **kwargs
        )
        sep1.grid(columnspan=5, sticky='ew')
        sep2.grid(columnspan=5, sticky='ew')
        separator = sep1, sep2
    else:
        sep1 = tk.Frame(
            master,
            bg='#909090',
            height=1,
            border=0,
            **kwargs
        )
        sep2 = tk.Frame(
            master,
            bg='#FFFFFF',
            height=1,
            border=0,
            **kwargs
        )
        sep1.grid(columnspan=5, sticky='ew')
        sep2.grid(columnspan=5, sticky='ew')
    return sep1, sep2

def default_canvas(master, **kwargs):
    if is_gnome_darkmode:
        canvas = tk.Canvas(
            master,
            bg='#333333',
            highlightthickness='0',
            **kwargs
        )
    else:
        canvas = tk.Canvas(
            master,
            highlightthickness='0',
            **kwargs
        )
    return canvas

def default_frame(master, **kwargs):
    if is_gnome_darkmode:
        frame = tk.Frame(
            master,
            bg='#333333',
            **kwargs
        )
    else:
        frame = tk.Frame(
            master,
            **kwargs
        )
    return frame

def default_label(master, *args, **kwargs):
    if is_gnome_darkmode:
        if 'offline' in args:
            info_font = '#A4A4A4'
        else:
            info_font = '#BDBDBD'
        label = tk.Label(
            master,
            bg='#333333',
            fg=info_font,
            highlightthickness=0,
            **kwargs
        )
    else:
        if 'offline' in args:
            info_font = '#333333'
        else:
            info_font = '#000000'
        label = tk.Label(
            master,
            fg=info_font,
            highlightthickness=0,
            **kwargs
        )
    return label

def default_button(master, *args, **kwargs):
    if is_gnome_darkmode:
        if 'offline' in args:
            info_font = '#A4A4A4'
        else:
            info_font = '#BDBDBD'
        button = tk.Button(
            master,
            bg='#333333',
            fg=info_font,
            activebackground='#3F3F3F',
            activeforeground=info_font,
            disabledforeground=info_font,
            highlightthickness=0,
            relief='flat',
            border=0,
            **kwargs
        )
    else:
        if 'offline' in args:
            info_font = '#333333'
        else:
            info_font = '#000000'
        button = tk.Button(
            master,
            highlightthickness=0,
            fg=info_font,
            activeforeground=info_font,
            disabledforeground=info_font,
            relief='flat',
            border=0,
            **kwargs
        )
    return button

def save_window_size():
    if is_gnome:
        top_bar_height = 37
    else:
        top_bar_height = 0
    x = root.winfo_x()
    y = root.winfo_y() - top_bar_height
    width = root.winfo_width()
    height = root.winfo_height()
    geometry = f"{width}x{height}+{x}+{y}"
    twitchapi.change_settings_file('window_size', geometry)

def initiate_window_dimensions():
    """Returns a default window size or user-adjusted window size and position
    """
    try:
        return twitchapi.get_setting('window_size')
    except:
        return f'285x450'

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
root = tk.Tk(className='Wince')
root.title("Wince")
root.geometry(initiate_window_dimensions())
root.minsize(285, 360)
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

# Detect GNOME to account for top bar in window position:
is_gnome = twitchapi.gnome_check
root.protocol("WM_DELETE_WINDOW", lambda: (
                                            save_window_size(),
                                            root.destroy()
                                            )
                )

# Fonts:
small_font = ('', 10)
cantarell_12 = ('Cantarell', 12)
cantarell_12_bold = ('Cantarell', 12, 'bold')
cantarell_13_bold = ('Cantarell', 13, 'bold')

# Detect Dark mode:
is_gnome_darkmode = twitchapi.detect_darkmode_gnome()

if is_gnome_darkmode:
    style = ttk.Style(root)
    style.configure('Vertical.TScrollbar',
                    gripcount=0,
                    relief='flat',
                    troughrelief='flat',
                    width=14,
                    groovewidth=14,
                    arrowsize=14,
                    background="#2c2c2c",
                    troughcolor="#363636",
                    arrowcolor="#BDBDBD"
                    )
    style.map("Vertical.TScrollbar", background=[("active", "#222222")])
else:
    style = ttk.Style(root)
    style.configure('Vertical.TScrollbar',
                    gripcount=0,
                    relief='flat',
                    troughrelief='flat',
                    width=14,
                    groovewidth=14,
                    arrowsize=14
                    )

# Import icons:
icon_files = twitchapi.icon_paths()
if is_gnome_darkmode:
    light = '_light'
else:
    light = ''
unfollow_icon = tk.PhotoImage(file=icon_files[f'unfollow_icon{light}'])
vod_icon = tk.PhotoImage(file=icon_files[f'vod_icon{light}'])
streaming_icon = tk.PhotoImage(file=icon_files['streaming_icon'])
offline_icon = tk.PhotoImage(file=icon_files['offline_icon'])
play_icon = tk.PhotoImage(file=icon_files[f'play_icon{light}'])
close_icon = tk.PhotoImage(file=icon_files[f'close_icon{light}'])
settings_icon = tk.PhotoImage(file=icon_files[f'settings_icon{light}'])

expand_icon = tk.PhotoImage(file=icon_files[f'expand_icon{light}'])
collapse_icon = tk.PhotoImage(file=icon_files[f'collapse_icon{light}'])

app_icon = tk.PhotoImage(file=icon_files['app_icon'])
root.iconphoto(False, app_icon)

# Variables to collect stream info
# and settings value to show info for all streamers:
stream_info_status = {}
stream_info_content = {}
preset_info_setting = tk.StringVar()
preset_info_setting = twitchapi.get_setting('show_info_preset')
current_info_setting = twitchapi.get_setting('show_info')

current_vod_panel = ''
vod_info_status = {}
vod_info_content = {}

custom_menu_bar()
draw_main()
root.mainloop()