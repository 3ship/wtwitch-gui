#!/usr/bin/env python

import webbrowser
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import initialize
import conf
import assets
import dialogs
import refresh


def vod_panel(streamer):
    '''Draw 2 columns for the watch buttons and timestamps/stream length of 
    the last 20 VODs. Clicking the timestamps or expand button shows title of
    the VOD(s).'''
    global current_vod_panel, vod_title_status, vod_title_content, vod_meta_frame


    vods = conf.fetch_vods(streamer)

    if len(vods[0]) == 0:
        messagebox.showinfo(
            title=f"No VODs", message=f"{streamer} has no VODs", parent=root
        )
        return

    # Indicate that a vod panel is open, so titles can be expanded/collapsed
    current_vod_panel = streamer

    # Stores, which VOD titles are currently expanded:
    vod_title_status = {}
    # Stores the VOD titles:
    vod_title_content = {}

    vod_meta_frame = assets.default_frame(root)
    vod_meta_frame.grid(column=0, row=1, sticky='nsew')
    vod_meta_frame.columnconfigure(0, weight=1)
    vod_meta_frame.rowconfigure(1, weight=1)

    # Header with close button and label
    header_frame = assets.default_frame(vod_meta_frame)
    header_frame.grid(column=0, row=0, sticky='nsew')
    header_frame.columnconfigure(1, weight=1)
    assets.default_button(
        header_frame, image=close_icon, command=lambda: close_vod_panel()
    ).grid(column=0, row=0, sticky='nw', ipady=12, ipadx=12)
    assets.default_label(header_frame, text=f"{streamer}'s VODs").grid(column=1, row=0)
    separator = assets.default_separator(header_frame, start_row=1)

    vod_scrollbar_frame = assets.default_frame(vod_meta_frame)
    vod_scrollbar_frame.grid(column=0, row=1, sticky='nsew')
    vod_scrollbar_frame.columnconfigure(0, weight=1)
    vod_scrollbar_frame.rowconfigure(0, weight=1)

    global vod_canvas
    vod_canvas = assets.default_canvas(vod_scrollbar_frame)
    vod_scrollbar = ttk.Scrollbar(
        vod_scrollbar_frame, orient="vertical", command=vod_canvas.yview
    )
    vod_canvas.grid(row=0, column=0, sticky="nsew")
    vod_scrollbar.grid(row=0, column=1, sticky="ns")
    vod_canvas.configure(yscrollcommand=vod_scrollbar.set)

    global vod_frame
    vod_frame = assets.default_frame(vod_scrollbar_frame)
    vod_frame.grid(column=0, row=0, sticky='nsew')
    vod_frame.columnconfigure(1, weight=1)

    # Pass vod number to conf.start_vod()
    vod_number = 1
    # Start at 0, increment by 4 (button row, title, two rows for separator)
    count_vod_rows = 0
    count_vod_rows_increment = 4

    for timestamp, title, length in zip(vods[0], vods[1], vods[2]):
        # Individual VOD titles are collapsed by default:
        vod_title_status[count_vod_rows] = False
        
        # Watch button to open VOD in media player:
        watch_button = assets.default_button(
            vod_frame, image=play_icon, 
            command=lambda s=streamer, v=vod_number: [conf.start_vod(s, v)]
        )
        watch_button.grid(column=0, row=count_vod_rows, sticky='nesw', 
                          ipadx=12, ipady=6)
        
        # Expand all titles, if the button in the main menu has been toggled:
        if current_expand_setting in ['all', 'online']:
            timestamp_button = assets.default_button(
                vod_frame, text=f"{timestamp} {length}", anchor='w', 
                state='disabled', font=assets.font_10
            )
            vod_title(vod_frame, count_vod_rows, title)
        # Otherwise collapse all and make them accessible through the timestamp:
        else:
            timestamp_button = assets.default_button(
                vod_frame, text=f"{timestamp} {length}", 
                command=lambda v=vod_frame, c=count_vod_rows, t=title: vod_title(v, c, t), 
                font=assets.font_10, anchor='w'
            )
        timestamp_button.grid(column=1, row=count_vod_rows, sticky='nesw')

        # Don't add a separator after the last item
        if vod_number != len(vods[0]):
            separator = assets.default_separator(vod_frame,
                                                start_row=count_vod_rows+2)

        vod_number += 1
        count_vod_rows += count_vod_rows_increment

    vod_canvas_window = vod_canvas.create_window((0, 0), window=vod_frame, anchor="nw")
    # Observe window resizes to stretch the content inside:
    vod_canvas.bind("<Configure>", lambda e: resize_canvas(e, vod_canvas, 
                                                         vod_canvas_window))
    # Bind mousewheel to VOD canvas:
    vod_canvas.bind_all("<Button-4>", lambda e: on_mouse_wheel(e, vod_canvas))
    vod_canvas.bind_all("<Button-5>", lambda e: on_mouse_wheel(e, vod_canvas))
    vod_canvas.bind_all("<MouseWheel>", lambda e: on_mouse_wheel_windows(e, 
                                                                        vod_canvas))


def vod_title(parent, c, title):
    '''Adds a row with the VOD title below the timestamp button, if it doesn't
    exist yet. Removes it, if it already exists. This allows the timestamp
    button to toggle between both states.'''
    if not vod_title_status[c]:
        vod_title_content[c] = assets.default_label(parent,
                                            text=f'{title}',
                                            justify='left',
                                            anchor='w')
        vod_title_content[c].grid(row=c+1, column=0, columnspan=3, sticky='w',
                                    padx=10)
        vod_title_status[c] = True
    else:
        vod_title_content[c].grid_remove()
        vod_title_status[c] = False


def refresh_vod_panel(streamer):
    ''' Called by refrefresh_stream_frame_quiet() when the info toggle in the
    main menu is (de)activated'''
    for widget in vod_meta_frame.winfo_children():
        widget.destroy()
    vod_panel(streamer)


def close_vod_panel():
    '''We need to make sure, the stream panel gets its scroll function back'''
    global vod_meta_frame, vod_canvas, current_vod_panel
    try:
        if vod_meta_frame.winfo_exists():
            vod_meta_frame.forget()
            vod_meta_frame.destroy()
        vod_canvas.unbind_all("<Configure>")
        vod_canvas.unbind_all("<Button-4>")
        vod_canvas.unbind_all("<Button-5>")
        vod_canvas.unbind_all("<MouseWheel>")
    except Exception as e:
        print("Error while closing VOD panel:", e)
    
    current_vod_panel = None  # Reset current_vod_panel

    # Currently necessary, because the info toggle makes the stream panel
    # disappear:
    stream_meta_frame.destroy()
    create_meta_frame()
    refresh.update_canvas(stream_canvas)


def stream_buttons():
    global stream_info_visible, stream_info_content
    global weblink_visible, weblink_content
    global extra_buttons_visible, extra_buttons_content

    online_streamers = streamer_status[0]
    offline_streamers = streamer_status[1]
    count_rows = 0
    count_rows_increment = 6

    # Initialize or clear dictionaries
    stream_info_visible = {}
    stream_info_content = {}
    weblink_visible = {}
    weblink_content = {}
    extra_buttons_visible = {}
    extra_buttons_content = {}

    for package in online_streamers:
        watch_button = assets.default_button(
            stream_frame, image=streaming_icon,
            command=lambda s=package[0]: [conf.start_stream(s)]
        )
        watch_button.grid(column=0, row=count_rows, sticky='nsew', ipadx=6, ipady=8)
        stream_info_visible[count_rows] = False
        weblink_visible[count_rows] = False
        extra_buttons_visible[count_rows] = False

        info_button = assets.default_button(
            stream_frame, text=package[1], anchor='w', font=assets.font_13_b,
            command=lambda cr=count_rows, s=package[0], l=package[1], c=package[2],
            t=package[3], v=package[4]:
            [stream_online_info(cr, l, c, t, v), stream_extra_buttons(s, cr)]
        )
        info_button.grid(column=1, row=count_rows, sticky='nsew')

        if current_expand_setting in ['all', 'online']:
            watch_button.grid_configure(rowspan=2)
            info_button.config(state='disabled')
            stream_extra_buttons(package[0], count_rows)
            stream_online_info(count_rows, package[1], package[2], package[3], package[4])
        else:
            if extra_buttons_always_visible.get() == 'yes':
                stream_extra_buttons(package[0], count_rows)
            else:
                info_button.grid_configure(columnspan=4)

        separator = assets.default_separator(stream_frame,
                                            start_row=count_rows+4)
        count_rows += count_rows_increment

    for stream in offline_streamers:
        watch_button = assets.default_label(stream_frame, image=offline_icon)
        watch_button.grid(column=0, row=count_rows, sticky='nsew', ipadx=6, ipady=6)
        stream_info_visible[count_rows] = False
        weblink_visible[count_rows] = False
        extra_buttons_visible[count_rows] = False

        info_button = assets.default_button(
            stream_frame, 'offline', text=stream, anchor='w',
            font=assets.font_13_b, compound='left',
            command=lambda s=stream, c=count_rows:
            [stream_offline_info(s, c), stream_extra_buttons(s, c)]
        )

        info_button.grid(column=1, row=count_rows, sticky='nsew')

        if current_expand_setting == 'all':
            watch_button.grid_configure(rowspan=2)
            info_button.config(state='disabled')
            stream_extra_buttons(stream, count_rows)
            stream_offline_info(stream, count_rows)
        else:
            if extra_buttons_always_visible.get() == 'yes':
                stream_extra_buttons(stream, count_rows)
            else:
                info_button.grid_configure(columnspan=4)

        # Don't add separator after the last item
        total_streamers = len(online_streamers) + len(offline_streamers)
        total_items = total_streamers * count_rows_increment
        if count_rows != total_items - count_rows_increment:
            separator = assets.default_separator(stream_frame,
                                                    start_row=count_rows+4)
        count_rows += count_rows_increment

def stream_extra_buttons(streamer, count_rows):
    if not extra_buttons_visible[count_rows]:
        extra_buttons_content[count_rows] = {}

        extra_buttons_content[count_rows]['unfollow'] = assets.default_button(
            stream_frame, image=unfollow_icon,
            command=lambda s=streamer, c=count_rows+3: [stream_unfollow_dialog(s, c)]
        )
        extra_buttons_content[count_rows]['unfollow'].grid(column=2,
                                                        row=count_rows,
                                                        sticky='nsew',
                                                        ipadx=4)

        extra_buttons_content[count_rows]['web'] = assets.default_button(
            stream_frame, image=link_icon,
            command=lambda s=streamer, c=count_rows: stream_website_dialog(c, s)
        )
        extra_buttons_content[count_rows]['web'].grid(column=3,
                                                        row=count_rows,
                                                        sticky='nsew',
                                                        ipadx=4)

        extra_buttons_content[count_rows]['vods'] = assets.default_button(
            stream_frame, image=vod_icon,
            command=lambda s=streamer: vod_panel(s)
        )
        extra_buttons_content[count_rows]['vods'].grid(column=4,
                                                        row=count_rows,
                                                        sticky='nsew',
                                                        ipadx=6)

        extra_buttons_visible[count_rows] = True
    else:
        if extra_buttons_always_visible.get() == 'yes':
            return
        else:
            extra_buttons_content[count_rows]['unfollow'].grid_remove()
            extra_buttons_content[count_rows]['web'].grid_remove()
            extra_buttons_content[count_rows]['vods'].grid_remove()
            extra_buttons_visible[count_rows] = False
            

def stream_online_info(c, streamer, category, title, viewercount):
    if not stream_info_visible[c]:
        if c not in stream_info_content:
            stream_info_content[c] = assets.default_label(
                stream_frame, text=   f'Title: {title}\n'
                                    f'Category: {category}\n'
                                    f'Viewer count: {viewercount}', 
                justify='left', anchor='w'
            )
            stream_info_content[c].grid(
                row=c+1, column=1, columnspan=4, sticky='w', padx=10
            )
        else:
            stream_info_content[c].config(
                text=   f'Title: {title}\nCategory: {category}\n'
                        f'Viewer count: {viewercount}'
            )
            stream_info_content[c].grid()
        stream_info_visible[c] = True
    else:
        stream_info_content[c].grid_remove()
        stream_info_visible[c] = False
    refresh.update_canvas(stream_canvas)


def stream_offline_info(stream, c):
    if not stream_info_visible[c]:
        last_seen_text = f'Last seen: {conf.last_seen(stream)}'
        if c not in stream_info_content:
            stream_info_content[c] = assets.default_label(stream_frame, 'offline',
                                                   text=last_seen_text,
                                                   justify='left',
                                                   anchor='w')
            stream_info_content[c].grid(row=c+1,
                                        column=1,
                                        columnspan=4,
                                        sticky='w',
                                        padx=10)
        else:
            stream_info_content[c].config(text=last_seen_text)
            stream_info_content[c].grid()
        stream_info_visible[c] = True
    else:
        stream_info_content[c].grid_remove()
        stream_info_visible[c] = False
    refresh.update_canvas(stream_canvas)


def stream_website_dialog(c, streamer):
    if not weblink_visible[c]:
        if c not in weblink_content:
            weblink_content[c] = assets.default_frame(stream_frame)
            weblink_content[c].grid(row=c+2, column=1, columnspan=4)
            website_button = assets.default_button(
                weblink_content[c], text='Twitch',
                command=lambda s=streamer: webbrowser.open(f'http://www.twitch.tv/{s}')
            )
            website_button.grid(row=0, column=0, sticky='ew')
            webplayer_button = assets.default_button(
                weblink_content[c], text='Webplayer',
                command=lambda s=streamer: webbrowser.open(
                    f'https://player.twitch.tv/?channel={s}&parent=twitch.tv')
            )
            webplayer_button.grid(row=0, column=1, sticky='ew')
        else:
            weblink_content[c].grid()
        weblink_visible[c] = True
    else:
        weblink_content[c].grid_remove()
        weblink_visible[c] = False
    refresh.update_canvas(stream_canvas)


def stream_unfollow_dialog(streamer, row):
    '''Asks for confirmation, if the unfollow button is pressed. Rebuild the
    main panel, if confirmed.
    '''
    answer = dialogs.askyesno(stream_frame, stream_canvas, f'\nUnfollow {streamer}?', row)
    if answer:
        conf.unfollow_streamer(streamer)
        refresh_stream_frame_quiet()
    else:
        refresh.update_canvas(stream_canvas)


def menu_follow_dialog():
    '''Opens a text dialog and adds the entered string to the follow list.
    '''
    answer = dialogs.askstring(menu_frame, stream_canvas, 'Add streamer:')
    if answer is None or len(answer) == 0:
        return
    else:
        conf.follow_streamer(answer)
        refresh_stream_frame_quiet()


def menu_play_dialog():
    '''Opens a text dialog to play a custom stream
    '''
    streamer = dialogs.askstring(menu_frame, stream_canvas, 'Play a custom stream:')
    if streamer is None or len(streamer) == 0:
        return
    else:
        update = conf.start_stream(streamer)


def refresh_stream_frame_quiet():
    '''Refreshes the frame without running wtwitch c. Used by everything that
    only changes the layout.'''
    global streamer_status, current_vod_panel
    try:
        streamer_status = conf.extract_streamer_status()
    except Exception as e:
        dialogs.error_message(e)

    # Temporarily disable scroll command
    stream_canvas.configure(yscrollcommand=None)

    # Clear and repopulate main_frame
    for widget in stream_frame.winfo_children():
        widget.destroy()
    stream_buttons()  # Re-populate the main_frame

    stream_canvas.update_idletasks()  # Flush the event queue
    # Re-enable scroll command
    stream_canvas.configure(yscrollcommand=stream_scrollbar.set)
    refresh.update_canvas(stream_canvas)  # Update the canvas region

    # If a VOD panel is active, refresh it
    if current_vod_panel:
        refresh_vod_panel(current_vod_panel)


def refresh_stream_frame():
    '''Runs wtwitch c and then rebuilds the main panel.'''
    conf.check_status()
    global streamer_status
    try:
        streamer_status = conf.extract_streamer_status()
    except Exception as e:
        dialogs.error_message(e)

    for widget in stream_frame.winfo_children():
        widget.destroy()
    stream_buttons()
    refresh.update_canvas(stream_canvas)


def resize_canvas(event, canvas, window):
    if canvas.winfo_exists():
        canvas.itemconfig(window, width=event.width)
        canvas.configure(scrollregion=canvas.bbox("all"))


def on_mouse_wheel(event, canvas):
    if event.num == 4 or event.delta > 0:
        canvas.yview_scroll(-1, "units")
    elif event.num == 5 or event.delta < 0:
        canvas.yview_scroll(1, "units")


def on_mouse_wheel_windows(event, canvas):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")


def create_meta_frame():
    '''The main window. Calls streamer_buttons() twice, to draw buttons for 
    online and offline streamers.'''
    
    global stream_meta_frame
    stream_meta_frame = assets.default_frame(root)
    stream_meta_frame.grid(row=1, column=0, sticky='nsew')
    stream_meta_frame.columnconfigure(0, weight=1)
    stream_meta_frame.rowconfigure(0, weight=1)
    
    global stream_canvas
    stream_canvas = assets.default_canvas(stream_meta_frame)
    stream_canvas.grid(row=0, column=0, sticky="nsew")
    stream_canvas.columnconfigure(0, weight=1)
    stream_canvas.rowconfigure(0, weight=1)
    
    global stream_scrollbar
    stream_scrollbar = ttk.Scrollbar(
        stream_meta_frame, orient="vertical", command=stream_canvas.yview
    )
    stream_scrollbar.grid(row=0, column=1, sticky="ns")
    stream_canvas.configure(yscrollcommand=stream_scrollbar.set)
    
    global stream_frame
    stream_frame = assets.default_frame(stream_canvas)
    stream_frame.grid(row=0, column=0, sticky='nsew')
    stream_frame.columnconfigure(1, weight=1)
    
    global stream_canvas_window
    stream_canvas_window = stream_canvas.create_window(
        (0, 0), window=stream_frame, anchor="nw"
    )
    stream_canvas.bind(
        "<Configure>", lambda e: resize_canvas(e, stream_canvas, stream_canvas_window)
    )
    stream_canvas.bind_all("<Button-4>", lambda e: on_mouse_wheel(e, stream_canvas))
    stream_canvas.bind_all("<Button-5>", lambda e: on_mouse_wheel(e, stream_canvas))
    stream_canvas.bind_all("<MouseWheel>", lambda e: on_mouse_wheel_windows(e, 
                                                                         stream_canvas))
    # Draw main content:
    stream_buttons()
    refresh.update_canvas(stream_canvas, True)  # Force update the canvas scroll region


def settings_custom_player():
    '''Opens a dialog to set a custom media player.
    '''
    new_player = dialogs.askstring(settings_frame, stream_canvas,
                                'Enter your media player:',
                                initial_value=conf.check_config()[0]
                                )
    if new_player is None or len(new_player) == 0:
        return
    else:
        conf.adjust_config('player', new_player)


def settings_custom_quality():
    '''Opens a dialog to set a custom stream quality.
    '''
    new_quality = dialogs.askstring(settings_frame, stream_canvas,
                                '\n Options: 1080p60, 720p60, 720p, 480p, \n'
                                ' 360p, 160p, best, worst, and audio_only \n'
                                '\n'
                                ' Specify fallbacks separated by a comma: \n'
                                ' E.g. "720p,480p,worst" \n',
                                initial_value=conf.check_config()[1],
                                )
    if new_quality is None or len(new_quality) == 0:
        return
    else:
        conf.adjust_config('quality', new_quality)


def settings_info_preset(value):
    conf.change_settings_file('show_info_preset', value)
    global current_expand_setting
    preset_info_setting = conf.get_setting('show_info_preset')
    
    if preset_info_setting != current_expand_setting and current_expand_setting != 'no':
        conf.change_settings_file('show_info', value)
        current_expand_setting = preset_info_setting
        refresh_stream_frame_quiet()


def settings_extrabuttons_preset(value):
    if conf.get_setting('extra_buttons') != value:
        conf.change_settings_file('extra_buttons', value)
        global extra_buttons_always_visible
        extra_buttons_always_visible.set(conf.get_setting('extra_buttons'))
        refresh_stream_frame_quiet()


def refresh_settings_window():
    global settings_window
    for widget in settings_window.winfo_children():
        widget.destroy()
    create_settings_frame()


def open_settings_window(root):
    global settings_window
    settings_window = tk.Toplevel(root)
    settings_window.grid_rowconfigure(0, weight=1)
    settings_window.grid_columnconfigure(0, weight=1)
    settings_window.title('Settings')
    settings_window.transient(root)
    settings_window.grab_set()
    create_settings_frame()


def create_settings_frame():
    '''Opens a toplevel window with four settings options.'''

    # Global variables
    global settings_window, settings_frame

    global preset_expand_setting, extra_buttons_always_visible, theme_setting
    
    global selected_player, selected_quality
    selected_player = tk.StringVar()
    selected_quality = tk.StringVar()

    # Check configurations and set default values
    if conf.check_config()[0] in ['mpv', 'vlc']:
        selected_player.set(conf.check_config()[0])
    else:
        selected_player.set('custom')

    if conf.check_config()[1] in [
        'best', '720p,720p60,480p,best', '480p,worst'
    ]:
        selected_quality.set(conf.check_config()[1])
    else:
        selected_quality.set('custom')

    settings_frame = assets.default_frame(settings_window)
    settings_frame.grid(sticky='nesw', ipady=10, ipadx=10)
    settings_frame.grid_rowconfigure(0, weight=1)
    settings_frame.grid_columnconfigure(0, weight=1)

    # Play settings frame
    player_frame = assets.default_frame(settings_frame)
    player_frame.grid(row=0, column=0, sticky='nesw', padx=20, pady=4)
    player_label = assets.default_label(player_frame, text='Media player:')
    player_label.grid(row=0, column=0, sticky='nsw', ipady=10)
    
    pick_mpv = assets.default_radiobutton(
        player_frame, text='mpv', value='mpv', variable=selected_player,
        command=lambda: conf.adjust_config('player', 'mpv')
    )
    pick_mpv.grid(row=1, column=0, sticky='nesw')
    
    pick_vlc = assets.default_radiobutton(
        player_frame, text='VLC', value='vlc', variable=selected_player,
        command=lambda: conf.adjust_config('player', 'vlc')
    )
    pick_vlc.grid(row=2, column=0, sticky='nesw')
    
    pick_custom_player = assets.default_radiobutton(
        player_frame, text='Custom', value='custom', variable=selected_player,
        command=lambda: settings_custom_player()
    )
    pick_custom_player.grid(row=3, column=0, sticky='nesw')

    # Quality settings frame
    quality_frame = assets.default_frame(settings_frame)
    quality_frame.grid(row=0, column=1, sticky='nesw', padx=20, pady=4)
    quality_label = assets.default_label(quality_frame, text='Video quality:')
    quality_label.grid(row=0, column=0, sticky='nsw', ipady=10)
    
    high_quality = assets.default_radiobutton(
        quality_frame, text='High', value='best', variable=selected_quality,
        command=lambda: conf.adjust_config('quality', 'best')
    )
    high_quality.grid(row=1, column=0, sticky='nesw')
    
    mid_quality = assets.default_radiobutton(
        quality_frame, text='Medium', value='720p,720p60,480p,best',
        variable=selected_quality,
        command=lambda: conf.adjust_config(
            'quality', '720p,720p60,480p,best'
        )
    )
    mid_quality.grid(row=2, column=0, sticky='nesw')
    
    low_quality = assets.default_radiobutton(
        quality_frame, text='Low', value='480p,worst', variable=selected_quality,
        command=lambda: conf.adjust_config('quality', '480p,worst')
    )
    low_quality.grid(row=3, column=0, sticky='nesw')
    
    pick_custom_quality = assets.default_radiobutton(
        quality_frame, text='Custom', value='custom', variable=selected_quality,
        command=lambda: settings_custom_quality()
    )
    pick_custom_quality.grid(row=4, column=0, sticky='nesw')

    # Separator
    separator1 = assets.default_separator(settings_frame, start_row=2)

    # Info settings frame
    info_frame = assets.default_frame(settings_frame)
    info_frame.grid(row=4, column=1, sticky='nesw', padx=20, pady=4)
    info_label = assets.default_label(info_frame, text='Expand info:')
    info_label.grid(row=0, column=0, sticky='nsw', ipady=10)
    
    all_info = assets.default_radiobutton(
        info_frame, text='All', value='all', variable=preset_expand_setting,
        command=lambda: [settings_info_preset('all')]
    )
    all_info.grid(row=1, column=0, sticky='nesw')
    
    only_online_info = assets.default_radiobutton(
        info_frame, text='Only online', value='online',
        variable=preset_expand_setting,
        command=lambda: [settings_info_preset('online')]
    )
    only_online_info.grid(row=2, column=0, sticky='nesw')

    # Always show unfollow/web/VOD buttons?
    extra_frame = assets.default_frame(settings_frame)
    extra_frame.grid(row=4, column=0, sticky='nesw', padx=20, pady=4)
    extra_label = assets.default_label(extra_frame, text=  'Always show\n'
                                                    'all buttons:')
    extra_label.grid(row=0, column=0, sticky='nsw', ipady=10)
    
    show_extra_yes = assets.default_radiobutton(
        extra_frame, text='Yes', value='yes', variable=extra_buttons_always_visible,
        command=lambda: [settings_extrabuttons_preset('yes')]
    )
    show_extra_yes.grid(row=1, column=0, sticky='nesw')
    
    show_extra_no = assets.default_radiobutton(
        extra_frame, text='No', value='no', variable=extra_buttons_always_visible,
        command=lambda: [settings_extrabuttons_preset('no')]
    )
    show_extra_no.grid(row=2, column=0, sticky='nesw')

    separator2 = assets.default_separator(settings_frame, start_row=5)

    # Theme settings frame
    theme_frame = assets.default_frame(settings_frame)
    theme_frame.grid(row=7, column=0, sticky='nesw', padx=20, pady=4, columnspan=2)
    theme_label = assets.default_label(theme_frame, text='Theme:')
    theme_label.grid(row=0, column=0, sticky='nsw', ipady=10)
    
    # Extract themes from properties dictionary and edit their names
    themes = {k.replace('_', ' ').title(): k for k in assets.properties.keys()}

    row_col_tracker = [1, 1]  # Row counters for columns 0 and 1

    for i, (theme, value) in enumerate(themes.items()):
        col = i % 2  # Distribute themes, alternating between two columns
        row = row_col_tracker[col]
        row_col_tracker[col] += 1
        rb = assets.default_radiobutton(
            theme_frame,
            text=theme,
            value=value,
            variable=theme_setting,
            command=lambda v=value: settings_theme_switch(v)
        )
        rb.grid(row=row, column=col, sticky='nesw', padx=20 if col == 1 else 0)


def settings_theme_switch(value):
    conf.change_settings_file('theme', value)
    global theme_setting
    theme_setting = tk.StringVar()
    theme_setting.set(conf.get_setting('theme'))
    assets.current_theme = value
    assets.theme = assets.properties[assets.current_theme]
    assets.scrollbar_presets(root)
    get_icons()
    menu_frame.destroy()
    create_menu_frame()
    stream_meta_frame.destroy()
    create_meta_frame()
    settings_frame.destroy()
    create_settings_frame()


def switch_info_toggle_icon(n):
    global current_expand_setting
    global current_quick_toggle_icon
    global expand_b
    if current_expand_setting == 'no':
        current_quick_toggle_icon = expand_icon
    else:
        current_quick_toggle_icon = collapse_icon
    if n == 1:
        expand_b.config(image=current_quick_toggle_icon)
    else:
        return current_quick_toggle_icon


def menu_info_toggle():
    global current_expand_setting
    if current_expand_setting == 'no':
        conf.change_settings_file('show_info', preset_expand_setting.get())
    else:
        conf.change_settings_file('show_info', 'no')
    current_expand_setting = conf.get_setting('show_info')
    refresh_stream_frame_quiet()


def create_menu_frame():
    global current_quick_toggle_icon
    current_quick_toggle_icon = switch_info_toggle_icon(0)
    global menu_frame
    menu_frame = assets.default_frame(root)
    menu_frame.grid(row=0, column=0, sticky='nesw')
    menu_frame.columnconfigure(3, weight=1)
    refresh_b = assets.default_button(menu_frame,
                    image=refresh_icon,
                    font=assets.font_12_b,
                    command=lambda: refresh_stream_frame()
                    )
    refresh_b.grid(row=0, column=0, sticky='nsw', ipadx=18, ipady=6)
    follow_b = assets.default_button(menu_frame,
                    image=follow_icon,
                    font=assets.font_12,
                    command=lambda: menu_follow_dialog()
                    )
    follow_b.grid(row=0, column=1, sticky='nsw', ipadx=18, ipady=6)
    play_b = assets.default_button(menu_frame,
                    image=play_stream_icon,
                    font=assets.font_12,
                    command=lambda: menu_play_dialog()
                    )
    play_b.grid(row=0, column=2, sticky='nsw', ipadx=18, ipady=6)
    settings_b = assets.default_button(menu_frame,
                    image=settings_icon,
                    font=assets.font_12,
                    command=lambda: open_settings_window(root)
                    )
    settings_b.grid(row=0, column=3, sticky='nsw', ipadx=18, ipady=6)
    global expand_b
    expand_b = assets.default_button(menu_frame,
                    image=current_quick_toggle_icon,
                    font=assets.font_12
                    )
    expand_b.grid(row=0, column=4, sticky='nsw', ipadx=4)
    expand_b.configure(command=lambda: [
                                        menu_info_toggle(),
                                        switch_info_toggle_icon(1)
                                        ]
                        )
    sep = assets.default_separator(menu_frame, start_row=5)


def save_window_size():
    if conf.is_gnome:
        top_bar_height = 37
    else:
        top_bar_height = 0
    x = root.winfo_x()
    y = root.winfo_y() - top_bar_height
    width = root.winfo_width()
    height = root.winfo_height()
    geometry = f"{width}x{height}+{x}+{y}"
    conf.change_settings_file('window_size', geometry)


def initiate_window_dimensions():
    """Returns a default window size or user-adjusted window size and position
    """
    return conf.get_setting('window_size')


def toggle_settings():
    """Checks if wtwitch prints offline streamers and color output. Latter is
    needed to filter wtwitch output with regex.
    """
    if conf.check_config()[2] == 'false':
        conf.adjust_config('colors', 'true')
    if conf.check_config()[3] == 'false':
        conf.adjust_config('printOfflineSubscriptions', 'true')


def get_icons():
    global app_icon
    # Import icons
    icon_files = conf.icon_paths()
    theme = conf.get_setting('theme')
    ending = assets.properties.get(theme, {}).get('icon_ending', '')
    
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
    
    # Assign to globals
    globals().update(icons)
    
    root.iconphoto(False, icons['app_icon'])


# Check the online/offline status once before window initialization:
conf.check_status()
try:
    streamer_status = conf.extract_streamer_status()
except Exception as e:
    dialogs.error_message(e)
# Make sure that colors in the terminal output are activated:
toggle_settings()

# Create the main window
root = tk.Tk(className='Wince')
root.title("Wince")
root.geometry(initiate_window_dimensions())
root.minsize(210, 360)
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.protocol("WM_DELETE_WINDOW", lambda: (save_window_size(),
                                        root.destroy()))


# Variables to collect stream info
# and settings value to show info for all streamers:
stream_info_visible = {}
stream_info_content = {}
preset_expand_setting = tk.StringVar()
preset_expand_setting.set(conf.get_setting('show_info_preset'))
current_expand_setting = conf.get_setting('show_info')

# Store whether the weblink buttons are currently displayed:
weblink_visible = {}
weblink_content = {}

extra_buttons_visible = {}
extra_buttons_content = {}
extra_buttons_always_visible = tk.StringVar()
extra_buttons_always_visible.set(conf.get_setting('extra_buttons'))

# Saves the name of the stream, whose VOD panel is currently shown, if present
current_vod_panel = None


# Set to 'dark', 'light' or 'system':
theme_setting = tk.StringVar()
theme_setting.set(conf.get_setting('theme'))


assets.scrollbar_presets(root)
get_icons()

create_menu_frame()
create_meta_frame()
root.mainloop()