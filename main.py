#!/usr/bin/env python

import webbrowser
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import twitchapi


def vod_panel(streamer):
    '''Draw 2 columns for the watch buttons and timestamps/stream length of 
    the last 20 VODs.'''
    global current_vod_panel, vod_info_status, vod_info_content, vw_frame
    current_vod_panel = streamer
    vods = twitchapi.fetch_vods(streamer)

    if len(vods[0]) == 0:
        messagebox.showinfo(
            title=f"No VODs", message=f"{streamer} has no VODs", parent=root
        )
        return

    vod_info_status = {}
    vod_info_content = {}

    vw_frame = default_frame(root)
    vw_frame.grid(column=0, row=1, sticky='nsew')
    vw_frame.columnconfigure(0, weight=1)
    vw_frame.rowconfigure(1, weight=1)

    header_frame = default_frame(vw_frame)
    header_frame.grid(column=0, row=0, sticky='nsew')
    header_frame.columnconfigure(1, weight=1)
    default_button(
        header_frame, image=close_icon, command=lambda: close_vod_panel()
    ).grid(column=0, row=0, sticky='nw', ipady=12, ipadx=12)
    default_label(header_frame, text=f"{streamer}'s VODs").grid(column=1, row=0)
    separator = default_separator(header_frame)
    separator[0].grid(row=1, columnspan=2)
    separator[1].grid(row=2, columnspan=2)

    met_frame = default_frame(vw_frame)
    met_frame.grid(column=0, row=1, sticky='nsew')
    met_frame.columnconfigure(0, weight=1)
    met_frame.rowconfigure(0, weight=1)

    global vw_canvas
    vw_canvas = default_canvas(met_frame)
    vw_scrollbar = ttk.Scrollbar(
        met_frame, orient="vertical", command=vw_canvas.yview
    )
    vw_canvas.grid(row=0, column=0, sticky="nsew")
    vw_scrollbar.grid(row=0, column=1, sticky="ns")
    vw_canvas.configure(yscrollcommand=vw_scrollbar.set)

    global vod_frame
    vod_frame = default_frame(met_frame)
    vod_frame.grid(column=0, row=0, sticky='nsew')
    vod_frame.columnconfigure(1, weight=1)

    vod_number = 1
    count_vod_rows = 3
    count_vod_rows_increment = 4
    for timestamp, title, length in zip(vods[0], vods[1], vods[2]):
        vod_info_status[count_vod_rows] = False
        watch_button = default_button(
            vod_frame, image=play_icon, 
            command=lambda s=streamer, v=vod_number: [twitchapi.start_vod(s, v)]
        )
        watch_button.grid(column=0, row=count_vod_rows, sticky='nesw', 
                          ipadx=12, ipady=6)

        if current_expand_setting == 'all' or current_expand_setting == 'online':
            timestamp_button = default_button(
                vod_frame, text=f"{timestamp} {length}", anchor='w', 
                state='disabled', font=small_font
            )
            vod_info(count_vod_rows, title)
        else:
            timestamp_button = default_button(
                vod_frame, text=f"{timestamp} {length}", 
                command=lambda c=count_vod_rows, t=title: vod_info(c, t), 
                font=small_font, anchor='w'
            )
        timestamp_button.grid(column=1, row=count_vod_rows, sticky='nesw')

        # Don't add a separator after the last item
        if vod_number != len(vods[0]):
            separator = default_separator(vod_frame)
            separator[0].grid(row=count_vod_rows + 2)
            separator[1].grid(row=count_vod_rows + 3)

        vod_number += 1
        count_vod_rows += count_vod_rows_increment

    global vw_canvas_window
    vw_canvas_window = vw_canvas.create_window(
        (0, 0), window=vod_frame, anchor="nw"
    )
    vw_canvas.bind("<Configure>", lambda e: resize_canvas(e, vw_canvas, 
                                                         vw_canvas_window))
    vw_canvas.bind_all("<Button-4>", lambda e: on_mouse_wheel(e, vw_canvas))
    vw_canvas.bind_all("<Button-5>", lambda e: on_mouse_wheel(e, vw_canvas))
    vw_canvas.bind_all("<MouseWheel>", lambda e: on_mouse_wheel_windows(e, 
                                                                        vw_canvas))


def vod_info(c, title):
    if not vod_info_status[c]:
        if c not in vod_info_content:
            vod_info_content[c] = default_label(vod_frame,
                                                text=f'{title}',
                                                justify='left',
                                                anchor='w')
            vod_info_content[c].grid(row=c+1,
                                     column=0,
                                     columnspan=3,
                                     sticky='w',
                                     padx=10)
        else:
            vod_info_content[c].config(text=f'{title}')
            vod_info_content[c].grid()
        vod_info_status[c] = True
    else:
        vod_info_content[c].grid_remove()
        vod_info_status[c] = False


def refresh_vod_panel(streamer):
    global vw_frame, stream_canvas
    if 'vw_frame' in globals() and vw_frame.winfo_exists():
        for widget in vw_frame.winfo_children():
            widget.destroy()
        vod_panel(streamer)


def close_vod_panel():
    global vw_frame, vw_canvas, current_vod_panel
    try:
        if vw_frame.winfo_exists():
            vw_frame.forget()
            vw_frame.destroy()
        vw_canvas.unbind_all("<Configure>")
        vw_canvas.unbind_all("<Button-4>")
        vw_canvas.unbind_all("<Button-5>")
        vw_canvas.unbind_all("<MouseWheel>")
    except Exception as e:
        print("Error while closing VOD panel:", e)
    
    current_vod_panel = None  # Reset current_vod_panel
    stream_canvas.destroy()
    create_meta_frame()
    update_meta_canvas()


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
        watch_button = default_button(
            stream_frame, image=streaming_icon,
            command=lambda s=package[0]: [twitchapi.start_stream(s)]
        )
        watch_button.grid(column=0, row=count_rows, sticky='nsew', ipadx=6, ipady=8)
        stream_info_visible[count_rows] = False
        weblink_visible[count_rows] = False
        extra_buttons_visible[count_rows] = False

        if current_expand_setting in ['all', 'online']:
            watch_button.grid_configure(rowspan=2)
            info_button = default_button(
                stream_frame, text=package[1], anchor='w', font=cantarell_13_bold,
                state='disabled'
            )
            stream_extra_buttons(package[0], count_rows)
            stream_online_info(
                count_rows, package[1], package[2], package[3], package[4]
            )
        else:
            if extra_buttons_always_visible.get() == 'yes':
                stream_extra_buttons(package[0], count_rows)
            info_button = default_button(
                stream_frame, text=package[1], anchor='w', font=cantarell_13_bold,
                command=lambda cr=count_rows, s=package[0], l=package[1], c=package[2],
                t=package[3], v=package[4]: [stream_online_info(cr, l, c, t, v),
                stream_extra_buttons(s, cr)]
            )
            
        info_button.grid(column=1, row=count_rows, sticky='nsew')

        separator = default_separator(stream_frame)
        separator[0].grid(row=count_rows + 4)
        separator[1].grid(row=count_rows + 5)
        count_rows += count_rows_increment

    for streamer in offline_streamers:
        watch_button = default_label(stream_frame, image=offline_icon)
        watch_button.grid(column=0, row=count_rows, sticky='nsew', ipadx=6, ipady=6)
        stream_info_visible[count_rows] = False
        weblink_visible[count_rows] = False
        extra_buttons_visible[count_rows] = False

        if current_expand_setting == 'all':
            watch_button.grid_configure(rowspan=2)
            info_button = default_button(
                stream_frame, 'offline', text=streamer, anchor='w', font=cantarell_13_bold,
                state='disabled'
            )
            stream_extra_buttons(streamer, count_rows)
            stream_offline_info(count_rows, streamer)
        else:
            if extra_buttons_always_visible.get() == 'yes':
                stream_extra_buttons(streamer, count_rows)
            info_button = default_button(
                stream_frame, 'offline', text=streamer, anchor='w', font=cantarell_13_bold,
                compound='left', command=lambda s=streamer, c=count_rows:
                [stream_offline_info(c, s), stream_extra_buttons(s, c)]
            )
            
        info_button.grid(column=1, row=count_rows, sticky='nsew')
        
        # Don't add separator after the last item
        total_streamers = len(online_streamers) + len(offline_streamers)
        total_items = total_streamers * count_rows_increment
        if count_rows != total_items - count_rows_increment:
            separator = default_separator(stream_frame)
            separator[0].grid(row=count_rows + 4)
            separator[1].grid(row=count_rows + 5)

        count_rows += count_rows_increment


def stream_extra_buttons(streamer, count_rows):
    if not extra_buttons_visible[count_rows]:
        extra_buttons_content[count_rows] = {}
        extra_buttons_content[count_rows]['unfollow'] = default_button(
            stream_frame, image=unfollow_icon,
            command=lambda s=streamer, c=count_rows+3: [stream_unfollow_dialog(s, c)]
        )
        extra_buttons_content[count_rows]['unfollow'].grid(column=2, row=count_rows, sticky='nsew', ipadx=4)
        extra_buttons_content[count_rows]['web'] = default_button(
            stream_frame, image=link_icon,
            command=lambda s=streamer, c=count_rows: stream_website_dialog(c, s)
        )
        extra_buttons_content[count_rows]['web'].grid(column=3, row=count_rows, sticky='nsew', ipadx=4)
        extra_buttons_content[count_rows]['vods'] = default_button(
            stream_frame, image=vod_icon,
            command=lambda s=streamer: vod_panel(s)
        )
        extra_buttons_content[count_rows]['vods'].grid(column=4, row=count_rows, sticky='nsew', ipadx=6)
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
            stream_info_content[c] = default_label(
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
    update_meta_canvas()


def stream_offline_info(c, streamer):
    if not stream_info_visible[c]:
        last_seen_text = f'Last seen: {twitchapi.last_seen(streamer)}'
        if c not in stream_info_content:
            stream_info_content[c] = default_label(stream_frame, 'offline',
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
    update_meta_canvas()


def stream_website_dialog(c, streamer):
    if not weblink_visible[c]:
        if c not in weblink_content:
            weblink_content[c] = default_frame(stream_frame)
            weblink_content[c].grid(row=c+2, column=1, columnspan=4)
            website_button = default_button(
                weblink_content[c], text='Twitch',
                command=lambda s=streamer: webbrowser.open(f'http://www.twitch.tv/{s}')
            )
            website_button.grid(row=0, column=0, sticky='ew')
            webplayer_button = default_button(
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
    update_meta_canvas()


def error_dialog(e):
    messagebox.showerror(title='Error',
                        message=f'{e}\n\n Check your internet connection!',
                        )


def stream_unfollow_dialog(streamer, row):
    '''Asks for confirmation, if the unfollow button is pressed. Rebuild the
    main panel, if confirmed.
    '''
    answer = add_askyesno_row(stream_frame, f'\nUnfollow {streamer}?', row)
    if answer:
        twitchapi.unfollow_streamer(streamer)
        refresh_stream_frame_quiet()


def menu_follow_dialog():
    '''Opens a text dialog and adds the entered string to the follow list.
    '''
    answer = add_askstring_row(menu_frame, 'Add streamer:')
    if answer is None or len(answer) == 0:
        return
    else:
        twitchapi.follow_streamer(answer)
        refresh_stream_frame_quiet()


def menu_play_dialog():
    '''Opens a text dialog to play a custom stream
    '''
    streamer = add_askstring_row(menu_frame, 'Play a custom stream:')
    if streamer is None or len(streamer) == 0:
        return
    else:
        update = twitchapi.start_stream(streamer)


def refresh_stream_frame_quiet():
    global streamer_status, current_vod_panel
    try:
        streamer_status = twitchapi.extract_streamer_status()
    except Exception as e:
        error_dialog(e)

    stream_canvas.update_idletasks()  # Flush the event queue
    stream_canvas.configure(yscrollcommand=None)  # Temporarily disable scroll command

    # Clear and repopulate main_frame
    for widget in stream_frame.winfo_children():
        widget.destroy()
    stream_buttons()  # Re-populate the main_frame

    stream_canvas.update_idletasks()  # Flush the event queue
    stream_canvas.configure(yscrollcommand=stream_scrollbar.set)  # Re-enable scroll command
    update_meta_canvas()  # Update the canvas region

    # If a VOD panel is active, refresh it
    if current_vod_panel:
        refresh_vod_panel(current_vod_panel)


def refresh_stream_frame():
    '''Runs wtwitch c and then rebuilds the main panel.'''
    twitchapi.check_status()
    global streamer_status, streamer_buttons_dict
    try:
        streamer_status = twitchapi.extract_streamer_status()
    except Exception as e:
        error_dialog(e)
    
    # Clear the dictionary before updating
    streamer_buttons_dict = {}

    for widget in stream_frame.winfo_children():
        widget.destroy()
    stream_buttons()
    update_meta_canvas()


def update_meta_canvas(force_update=False):
    if force_update or stream_canvas.bbox("all") != stream_canvas.bbox("view"):
        stream_canvas.update_idletasks()
        stream_canvas.configure(scrollregion=stream_canvas.bbox("all"))


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
    stream_meta_frame = default_frame(root)
    stream_meta_frame.grid(row=1, column=0, sticky='nsew')
    stream_meta_frame.columnconfigure(0, weight=1)
    stream_meta_frame.rowconfigure(0, weight=1)
    
    global stream_canvas
    stream_canvas = default_canvas(stream_meta_frame)
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
    stream_frame = default_frame(stream_canvas)
    stream_frame.grid(row=0, column=0, sticky='nsew')
    stream_frame.columnconfigure(1, weight=1)
    
    global meta_canvas_window
    meta_canvas_window = stream_canvas.create_window(
        (0, 0), window=stream_frame, anchor="nw"
    )
    stream_canvas.bind(
        "<Configure>", lambda e: resize_canvas(e, stream_canvas, meta_canvas_window)
    )
    stream_canvas.bind_all("<Button-4>", lambda e: on_mouse_wheel(e, stream_canvas))
    stream_canvas.bind_all("<Button-5>", lambda e: on_mouse_wheel(e, stream_canvas))
    stream_canvas.bind_all("<MouseWheel>", lambda e: on_mouse_wheel_windows(e, 
                                                                         stream_canvas))
    # Draw main content:
    stream_buttons()
    update_meta_canvas(True)  # Force update the canvas scroll region


def settings_custom_player():
    '''Opens a dialog to set a custom media player.
    '''
    new_player = add_askstring_row(settings_frame,
                                'Enter your media player:',
                                initial_value=twitchapi.check_config()[0]
                                )
    if new_player is None or len(new_player) == 0:
        return
    else:
        twitchapi.adjust_config('player', new_player)


def settings_custom_quality():
    '''Opens a dialog to set a custom stream quality.
    '''
    new_quality = add_askstring_row(settings_frame,
                                '\n Options: 1080p60, 720p60, 720p, 480p, \n'
                                ' 360p, 160p, best, worst, and audio_only \n'
                                '\n'
                                ' Specify fallbacks separated by a comma: \n'
                                ' E.g. "720p,480p,worst" \n',
                                initial_value=twitchapi.check_config()[1],
                                )
    if new_quality is None or len(new_quality) == 0:
        return
    else:
        twitchapi.adjust_config('quality', new_quality)


def settings_info_preset(value):
    twitchapi.change_settings_file('show_info_preset', value)
    global current_expand_setting
    preset_info_setting = twitchapi.get_setting('show_info_preset')
    
    if preset_info_setting != current_expand_setting and current_expand_setting != 'no':
        twitchapi.change_settings_file('show_info', value)
        current_expand_setting = preset_info_setting
        refresh_stream_frame_quiet()


def settings_extrabuttons_preset(value):
    if twitchapi.get_setting('extra_buttons') != value:
        twitchapi.change_settings_file('extra_buttons', value)
        global extra_buttons_always_visible
        extra_buttons_always_visible.set(twitchapi.get_setting('extra_buttons'))
        refresh_stream_frame_quiet()


def refresh_settings_window():
    global settings_window
    for widget in settings_window.winfo_children():
        widget.destroy()
    create_settings_frame()


def open_settings_window():
    global settings_window
    settings_window = tk.Toplevel(master=root)
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
    if twitchapi.check_config()[0] in ['mpv', 'vlc']:
        selected_player.set(twitchapi.check_config()[0])
    else:
        selected_player.set('custom')

    if twitchapi.check_config()[1] in [
        'best', '720p,720p60,480p,best', '480p,worst'
    ]:
        selected_quality.set(twitchapi.check_config()[1])
    else:
        selected_quality.set('custom')

    settings_frame = default_frame(settings_window)
    settings_frame.grid(sticky='nesw', ipady=10, ipadx=10)
    settings_frame.grid_rowconfigure(0, weight=1)
    settings_frame.grid_columnconfigure(0, weight=1)

    # Play settings frame
    player_frame = default_frame(settings_frame)
    player_frame.grid(row=0, column=0, sticky='nesw', padx=20, pady=4)
    player_label = default_label(player_frame, text='Media player:')
    player_label.grid(row=0, column=0, sticky='nsw', ipady=10)
    
    pick_mpv = default_radiobutton(
        player_frame, text='mpv', value='mpv', variable=selected_player,
        command=lambda: twitchapi.adjust_config('player', 'mpv')
    )
    pick_mpv.grid(row=1, column=0, sticky='nesw')
    
    pick_vlc = default_radiobutton(
        player_frame, text='VLC', value='vlc', variable=selected_player,
        command=lambda: twitchapi.adjust_config('player', 'vlc')
    )
    pick_vlc.grid(row=2, column=0, sticky='nesw')
    
    pick_custom_player = default_radiobutton(
        player_frame, text='Custom', value='custom', variable=selected_player,
        command=lambda: settings_custom_player()
    )
    pick_custom_player.grid(row=3, column=0, sticky='nesw')

    # Quality settings frame
    quality_frame = default_frame(settings_frame)
    quality_frame.grid(row=0, column=1, sticky='nesw', padx=20, pady=4)
    quality_label = default_label(quality_frame, text='Video quality:')
    quality_label.grid(row=0, column=0, sticky='nsw', ipady=10)
    
    high_quality = default_radiobutton(
        quality_frame, text='High', value='best', variable=selected_quality,
        command=lambda: twitchapi.adjust_config('quality', 'best')
    )
    high_quality.grid(row=1, column=0, sticky='nesw')
    
    mid_quality = default_radiobutton(
        quality_frame, text='Medium', value='720p,720p60,480p,best',
        variable=selected_quality,
        command=lambda: twitchapi.adjust_config(
            'quality', '720p,720p60,480p,best'
        )
    )
    mid_quality.grid(row=2, column=0, sticky='nesw')
    
    low_quality = default_radiobutton(
        quality_frame, text='Low', value='480p,worst', variable=selected_quality,
        command=lambda: twitchapi.adjust_config('quality', '480p,worst')
    )
    low_quality.grid(row=3, column=0, sticky='nesw')
    
    pick_custom_quality = default_radiobutton(
        quality_frame, text='Custom', value='custom', variable=selected_quality,
        command=lambda: settings_custom_quality()
    )
    pick_custom_quality.grid(row=4, column=0, sticky='nesw')

    # Separator to separate top and bottom frames
    separator = default_separator(settings_frame)
    separator[0].grid(row=2, columnspan=2)
    separator[1].grid(row=3, columnspan=2)

    # Info settings frame
    info_frame = default_frame(settings_frame)
    info_frame.grid(row=4, column=1, sticky='nesw', padx=20, pady=4)
    info_label = default_label(info_frame, text='Expand info:')
    info_label.grid(row=0, column=0, sticky='nsw', ipady=10)
    
    all_info = default_radiobutton(
        info_frame, text='All', value='all', variable=preset_expand_setting,
        command=lambda: [settings_info_preset('all')]
    )
    all_info.grid(row=1, column=0, sticky='nesw')
    
    only_online_info = default_radiobutton(
        info_frame, text='Only online', value='online',
        variable=preset_expand_setting,
        command=lambda: [settings_info_preset('online')]
    )
    only_online_info.grid(row=2, column=0, sticky='nesw')

    # Always show unfollow/web/VOD buttons?
    extra_frame = default_frame(settings_frame)
    extra_frame.grid(row=4, column=0, sticky='nesw', padx=20, pady=4)
    extra_label = default_label(extra_frame, text=  'Always show\n'
                                                    'all buttons')
    extra_label.grid(row=0, column=0, sticky='nsw', ipady=10)
    
    show_extra_yes = default_radiobutton(
        extra_frame, text='Yes', value='yes', variable=extra_buttons_always_visible,
        command=lambda: [settings_extrabuttons_preset('yes')]
    )
    show_extra_yes.grid(row=1, column=0, sticky='nesw')
    
    show_extra_no = default_radiobutton(
        extra_frame, text='No', value='no', variable=extra_buttons_always_visible,
        command=lambda: [settings_extrabuttons_preset('no')]
    )
    show_extra_no.grid(row=2, column=0, sticky='nesw')

    # Theme settings frame
    theme_frame = default_frame(settings_frame)
    theme_frame.grid(row=5, column=0, sticky='nesw', padx=20, pady=4)
    theme_label = default_label(theme_frame, text='Theme:')
    theme_label.grid(row=0, column=0, sticky='nsw', ipady=10)
    
    themes = {
        'GNOME Dark': 'gnome_dark',
        'GNOME Light': 'gnome_light',
        'Blues Dark': 'blues_dark',
        'Blues Light': 'blues_light',
        'Reds Dark': 'reds_dark',
        'Reds Light': 'reds_light',
        'Midnight': 'midnight'
    }

    row = 1
    for theme, value in themes.items():
        rb = default_radiobutton(theme_frame,
                            text=theme, value=value, variable=theme_setting,
                            command=lambda v=value: settings_theme_switch(v)
                            )
        rb.grid(row=row, column=0, sticky='nesw')
        row += 1


def settings_theme_switch(value):
    twitchapi.change_settings_file('theme', value)
    global is_dark_theme, theme_setting, current_theme, theme
    is_dark_theme = twitchapi.detect_dark_theme()
    theme_setting = tk.StringVar()
    theme_setting.set(twitchapi.get_setting('theme'))
    current_theme = value
    theme = theme_properties[current_theme]
    scrollbar_presets()
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
    return current_quick_toggle_icon


def menu_info_toggle():
    global current_expand_setting, current_vod_panel
    if current_expand_setting == 'no':
        twitchapi.change_settings_file('show_info', preset_expand_setting.get())
    else:
        twitchapi.change_settings_file('show_info', 'no')
    current_expand_setting = twitchapi.get_setting('show_info')
    refresh_stream_frame_quiet()

    # Check if a VOD panel is active
    if current_vod_panel:
        refresh_vod_panel(current_vod_panel)


def add_askyesno_row(frame, prompt, row):
    global current_yesno_frame
    if current_yesno_frame is not None:
        current_yesno_frame.destroy()
        current_yesno_frame = None

    def on_yes(event=None):
        nonlocal response
        response = True
        askyesno_frame.destroy()

    def on_no():
        nonlocal response
        response = False
        askyesno_frame.destroy()

    askyesno_frame = default_frame(frame)
    askyesno_frame.grid(row=row, column=0, columnspan=5)
    current_yesno_frame = askyesno_frame

    label = default_label(askyesno_frame, text=prompt)
    label.grid(row=0, column=0, padx=6, sticky='ew', columnspan=2)

    yes_button = default_button(askyesno_frame, text="Yes", command=on_yes)
    yes_button.grid(row=2, column=0, sticky='ew', pady=6)

    no_button = default_button(askyesno_frame, text="No", command=on_no)
    no_button.grid(row=2, column=1, sticky='ew')
    update_meta_canvas()
    response = None
    askyesno_frame.wait_window()
    update_meta_canvas()
    return response


def add_askstring_row(frame, prompt, initial_value=""):
    global current_query_frame
    if current_query_frame is not None:
        current_query_frame.destroy()
        current_query_frame = None

    def on_submit(event=None):
        nonlocal response
        response = entry.get()
        askstring_frame.destroy()

    def on_cancel():
        nonlocal response
        response = None
        askstring_frame.destroy()

    askstring_frame = default_frame(frame)
    askstring_frame.grid(row=1, column=0, columnspan=5)
    current_query_frame = askstring_frame
    label = default_label(askstring_frame, text=prompt)
    label.grid(row=0, column=0, padx=6, sticky='ew', columnspan=2)
    entry = tk.Entry(askstring_frame)
    entry.grid(row=1, column=0, padx=6, pady=4, columnspan=2)
    entry.bind("<Return>", on_submit)
    entry.insert(0, initial_value)
    entry.focus_set()
    cancel_button = default_button(askstring_frame,
                                    text="Cancel",
                                    command=on_cancel
                                    )
    cancel_button.grid(row=2, column=0, sticky='ew', pady=6)
    submit_button = default_button(askstring_frame,
                                    text="Enter",
                                    command=on_submit
                                    )
    submit_button.grid(row=2, column=1, sticky='ew')
    update_meta_canvas()
    response = None
    askstring_frame.wait_window()
    update_meta_canvas()
    return response


def create_menu_frame():
    global current_quick_toggle_icon
    current_quick_toggle_icon = switch_info_toggle_icon(0)
    global menu_frame
    menu_frame = default_frame(root)
    menu_frame.grid(row=0, column=0, sticky='nesw')
    menu_frame.columnconfigure(3, weight=1)
    refresh_b = default_button(menu_frame,
                    image=refresh_icon,
                    font=cantarell_12_bold,
                    command=lambda: refresh_stream_frame()
                    )
    refresh_b.grid(row=0, column=0, sticky='nsw', ipadx=18, ipady=6)
    follow_b = default_button(menu_frame,
                    image=follow_icon,
                    font=cantarell_12,
                    command=lambda: menu_follow_dialog()
                    )
    follow_b.grid(row=0, column=1, sticky='nsw', ipadx=18, ipady=6)
    play_b = default_button(menu_frame,
                    image=play_stream_icon,
                    font=cantarell_12,
                    command=lambda: menu_play_dialog()
                    )
    play_b.grid(row=0, column=2, sticky='nsw', ipadx=18, ipady=6)
    settings_b = default_button(menu_frame,
                    image=settings_icon,
                    font=cantarell_12,
                    command=lambda: open_settings_window()
                    )
    settings_b.grid(row=0, column=3, sticky='nsw', ipadx=18, ipady=6)
    global expand_b
    expand_b = default_button(menu_frame,
                    image=current_quick_toggle_icon,
                    font=cantarell_12
                    )
    expand_b.grid(row=0, column=4, sticky='nsw', ipadx=4)
    expand_b.configure(command=lambda: [
                                        menu_info_toggle(),
                                        switch_info_toggle_icon(1)
                                        ]
                        )
    sep = default_separator(menu_frame)
    sep[0].grid(row=5)
    sep[1].grid(row=6)


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
    sep1 = tk.Frame(master, bg=theme['separator_bg1'], height=1, borderwidth=1, relief="flat")
    sep2 = tk.Frame(master, bg=theme['separator_bg2'], height=1, borderwidth=1, relief="flat")
    
    sep1.grid(row=0, column=0, sticky='ew', columnspan=span)
    sep2.grid(row=1, column=0, sticky='ew', columnspan=span)
    
    return sep1, sep2


def default_canvas(master, **kwargs):
    return tk.Canvas(master, bg=theme['bg'], **base_widget_attributes, **kwargs)


def default_frame(master, **kwargs):
    return tk.Frame(master, bg=theme['bg'], **base_widget_attributes, **kwargs)


def default_label(master, *args, **kwargs):
    fg_color = theme['offline_fg'] if 'offline' in args else theme['fg']
    return tk.Label(master, bg=theme['bg'], fg=fg_color, **base_widget_attributes, **kwargs)


def default_button(master, *args, **kwargs):
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


def scrollbar_presets():
    scrollbar_width = 16
    style = ttk.Style(root)
    scrollbar_theme = theme['scrollbar']
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
    style.map("Vertical.TScrollbar", background=[("active", scrollbar_theme['active'])])


def get_icons():
    global unfollow_icon, vod_icon, streaming_icon, offline_icon, play_icon
    global close_icon, settings_icon, link_icon, expand_icon, collapse_icon
    global follow_icon, play_stream_icon, refresh_icon
    global app_icon
    # Import icons:
    icon_files = twitchapi.icon_paths()
    if is_dark_theme:
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
    link_icon = tk.PhotoImage(file=icon_files[f'link_icon{light}'])
    follow_icon = tk.PhotoImage(file=icon_files[f'follow_icon{light}'])
    play_stream_icon = tk.PhotoImage(file=icon_files[f'play_stream_icon{light}'])
    refresh_icon = tk.PhotoImage(file=icon_files[f'refresh_icon{light}'])

    expand_icon = tk.PhotoImage(file=icon_files[f'expand_icon{light}'])
    collapse_icon = tk.PhotoImage(file=icon_files[f'collapse_icon{light}'])

    app_icon = tk.PhotoImage(file=icon_files['app_icon'])
    root.iconphoto(False, app_icon)


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
    return twitchapi.get_setting('window_size')


def toggle_settings():
    """Checks if wtwitch prints offline streamers and color output. Latter is
    needed to filter wtwitch output with regex.
    """
    if twitchapi.check_config()[2] == 'false':
        twitchapi.adjust_config('colors', 'true')
    if twitchapi.check_config()[3] == 'false':
        twitchapi.adjust_config('printOfflineSubscriptions', 'true')





# Check the online/offline status once before window initialization:
twitchapi.check_status()
try:
    streamer_status = twitchapi.extract_streamer_status()
except Exception as e:
    error_dialog(e)
# Make sure that colors in the terminal output are activated:
toggle_settings()
# Create a Wince-specific settings file:
twitchapi.create_settings_file()

# Create the main window
root = tk.Tk(className='Wince')
root.title("Wince")
root.geometry(initiate_window_dimensions())
root.minsize(210, 360)
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

theme_properties = {
    'gnome_dark': {
        'bg': '#333333',
        'fg': '#BDBDBD',
        'offline_fg': '#A4A4A4',
        'activebackground': '#3F3F3F',
        'selectcolor': '#242424',
        'separator_bg1': '#252525',
        'separator_bg2': '#484848',
        'scrollbar': {
            'bg': '#2c2c2c',
            'trough': '#363636',
            'arrow': '#BDBDBD',
            'active': '#222222'
        }
    },
    'gnome_light': {
        'bg': '#FAFAFA',
        'fg': '#101010',
        'offline_fg': '#333333',
        'activebackground': '#EAEAEA',
        'selectcolor': '#FAFAFA',
        'separator_bg1': '#E3E3E3',
        'separator_bg2': '#FFFFFF',
        'scrollbar': {
            'bg': '#EFEFEF',
            'trough': '#DBDBDB',
            'arrow': '#2c2c2c',
            'active': '#FFFFFF'
        }
    },
    'blues_dark': {
        'bg': '#30343F',
        'fg': '#B0B7BF',
        'offline_fg': '#9CA3AF',
        'activebackground': '#39404F',
        'selectcolor': '#24292F',
        'separator_bg1': '#262A34',
        'separator_bg2': '#4B515F',
        'scrollbar': {
            'bg': '#2F3441',
            'trough': '#3A3F4C',
            'arrow': '#D27F7F',
            'active': '#5A6E73'
        }
    },
    'blues_light': {
        'bg': '#EAF5FB',
        'fg': '#0D1B2A',
        'offline_fg': '#2B3B52',
        'activebackground': '#D9E8EF',
        'selectcolor': '#C1D3DA',
        'separator_bg1': '#C4DDE9',
        'separator_bg2': '#E3F4FA',
        'scrollbar': {
            'bg': '#D4E8F1',
            'trough': '#BED5DC',
            'arrow': '#8A9BAA',
            'active': '#487A8B'
        }
    },
    'reds_dark': {
        'bg': '#402D2D',
        'fg': '#BDBDBD',
        'offline_fg': '#A4A4A4',
        'activebackground': '#4B3535',
        'selectcolor': '#7D2A2A',
        'separator_bg1': '#362525',
        'separator_bg2': '#5A3F3F',
        'scrollbar': {
            'bg': '#3A2C2C',
            'trough': '#4A2C2C',
            'arrow': '#D15656',
            'active': '#8A3F3F'
        }
    },
    'reds_light': {
        'bg': '#FFEDED',
        'fg': '#101010',
        'offline_fg': '#3B2B2B',
        'activebackground': '#F7DCDC',
        'selectcolor': '#FFA8A8',
        'separator_bg1': '#F4CFCF',
        'separator_bg2': '#FFE0E0',
        'scrollbar': {
            'bg': '#FDD5D5',
            'trough': '#F4BFBF',
            'arrow': '#BF3030',
            'active': '#E57373'
        }
    },
    'midnight': {
        'bg': '#121212',
        'fg': '#bbbbbb',
        'offline_fg': '#555555',
        'activebackground': '#1d1d1d',
        'selectcolor': '#555555',
        'separator_bg1': '#252525',
        'separator_bg2': '#353535',
        'scrollbar': {
            'bg': '#555555',
            'trough': '#1d1d1d',
            'arrow': '#252525',
            'active': '#353535'
        }
    }
}

# Base attributes for all widgets
base_widget_attributes = {
    'highlightthickness': 0,
    'relief': 'flat',
    'border': 0
}



# Variables to collect stream info
# and settings value to show info for all streamers:
stream_info_visible = {}
stream_info_content = {}
preset_expand_setting = tk.StringVar()
preset_expand_setting.set(twitchapi.get_setting('show_info_preset'))
current_expand_setting = twitchapi.get_setting('show_info')

# Store whether the weblink buttons are currently displayed:
weblink_visible = {}
weblink_content = {}

extra_buttons_visible = {}
extra_buttons_content = {}
extra_buttons_always_visible = tk.StringVar()
extra_buttons_always_visible.set(twitchapi.get_setting('extra_buttons'))

# Saves the name of the stream, whose VOD panel is currently shown, if present
current_vod_panel = ''

current_yesno_frame = None
current_query_frame = None


# Return True/False for dark theme:
is_dark_theme = twitchapi.detect_dark_theme()
# Set to 'dark', 'light' or 'system':
theme_setting = tk.StringVar()
theme_setting.set(twitchapi.get_setting('theme'))
# Only use dark/light for the time being:
current_theme = twitchapi.get_setting('theme')
# Retrieves colors from dictionary:
theme = theme_properties[current_theme]

scrollbar_presets()
get_icons()


create_menu_frame()
create_meta_frame()
root.mainloop()