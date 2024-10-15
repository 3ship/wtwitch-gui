#!/usr/bin/env python

import webbrowser
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import twitchapi

current_vod_panel = ''

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

        if vod_number != len(vods[0]):
            separator = default_separator(vod_frame)
            separator[0].grid(row=count_vod_rows + 2)
            separator[1].grid(row=count_vod_rows + 3)

        vod_number += 1
        count_vod_rows += 4

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
    global vw_frame, meta_canvas
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
    meta_canvas.destroy()
    draw_main()
    update_meta_canvas()

def streamer_buttons():
    global stream_info_status, stream_info_content
    global weblink_status, weblink_content

    online_streamers = streamer_status[0]
    offline_streamers = streamer_status[1]
    count_rows = 0

    # Initialize or clear dictionaries
    stream_info_status = {}
    stream_info_content = {}
    weblink_status = {}
    weblink_content = {}

    for package in online_streamers:
        watch_button = default_button(
            main_frame, image=streaming_icon,
            command=lambda s=package[0]: [twitchapi.start_stream(s)]
        )
        watch_button.grid(column=0, row=count_rows, sticky='nsew', ipadx=6, ipady=8)
        stream_info_status[count_rows] = False
        weblink_status[count_rows] = False

        if current_expand_setting == 'all' or current_expand_setting == 'online':
            watch_button.grid_configure(rowspan=2)
            info_button = default_button(
                main_frame, text=package[1], anchor='w', font=cantarell_13_bold,
                state='disabled'
            )
            online_info(
                count_rows, package[1], package[2], package[3], package[4]
            )
        else:
            info_button = default_button(
                main_frame, text=package[1], anchor='w', font=cantarell_13_bold,
                command=lambda cr=count_rows, s=package[1], c=package[2],
                t=package[3], v=package[4]: online_info(cr, s, c, t, v)
            )
            
        info_button.grid(column=1, row=count_rows, sticky='nsew')
        unfollow_b = default_button(
            main_frame, image=unfollow_icon,
            command=lambda s=package[0], c=count_rows+3: [unfollow_dialog(s, c)]
        )
        unfollow_b.grid(column=2, row=count_rows, sticky='nsew', ipadx=4)
        web_b = default_button(
            main_frame, image=link_icon,
            command=lambda s=package[0], c=count_rows: website_dialog(c, s)
        )
        web_b.grid(column=3, row=count_rows, sticky='nsew', ipadx=4)
        vod_b = default_button(
            main_frame, image=vod_icon,
            command=lambda s=package[0]: vod_panel(s)
        )
        vod_b.grid(column=4, row=count_rows, sticky='nsew', ipadx=6)
        
        separator = default_separator(main_frame)
        separator[0].grid(row=count_rows + 4)
        separator[1].grid(row=count_rows + 5)
        count_rows += 6

    for streamer in offline_streamers:
        watch_button = default_label(main_frame, image=offline_icon)
        watch_button.grid(column=0, row=count_rows, sticky='nsew', ipadx=6, ipady=6)
        stream_info_status[count_rows] = False
        weblink_status[count_rows] = False

        if current_expand_setting == 'all':
            watch_button.grid_configure(rowspan=2)
            info_button = default_button(
                main_frame, text=streamer, anchor='w', font=cantarell_13_bold,
                state='disabled'
            )
            offline_info(count_rows, streamer)
        else:
            info_button = default_button(
                main_frame, text=streamer, anchor='w', font=cantarell_13_bold,
                compound='left', command=lambda s=streamer, c=count_rows:
                offline_info(c, s)
            )
            
        info_button.grid(column=1, row=count_rows, sticky='nsew')
        unfollow_b = default_button(
            main_frame, image=unfollow_icon,
            command=lambda s=streamer, c=count_rows + 3: [unfollow_dialog(s, c)]
        )
        unfollow_b.grid(column=2, row=count_rows, sticky='nsew', ipadx=4)
        web_b = default_button(
            main_frame, image=link_icon,
            command=lambda s=streamer, c=count_rows: website_dialog(c, s)
        )
        web_b.grid(column=3, row=count_rows, sticky='nsew', ipadx=4)
        vod_b = default_button(
            main_frame, image=vod_icon,
            command=lambda s=streamer: vod_panel(s)
        )
        vod_b.grid(column=4, row=count_rows, sticky='nsew', ipadx=6)
        
        if count_rows != (len(online_streamers) + len(offline_streamers)) * 6 - 6:
            separator = default_separator(main_frame)
            separator[0].grid(row=count_rows + 4)
            separator[1].grid(row=count_rows + 5)
        count_rows += 6


def online_info(c, streamer, category, title, viewercount):
    if not stream_info_status[c]:
        if c not in stream_info_content:
            stream_info_content[c] = default_label(
                main_frame, text=   f'Title: {title}\n'
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
        stream_info_status[c] = True
    else:
        stream_info_content[c].grid_remove()
        stream_info_status[c] = False
    update_meta_canvas()


def offline_info(c, streamer):
    if not stream_info_status[c]:
        last_seen_text = f'Last seen: {twitchapi.last_seen(streamer)}'
        if c not in stream_info_content:
            stream_info_content[c] = default_label(main_frame,
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
        stream_info_status[c] = True
    else:
        stream_info_content[c].grid_remove()
        stream_info_status[c] = False
    update_meta_canvas()

def website_dialog(c, streamer):
    if not weblink_status[c]:
        if c not in weblink_content:
            weblink_content[c] = default_frame(main_frame)
            weblink_content[c].grid(row=c+2, column=1, columnspan=4)
            website_button = default_button(
                weblink_content[c], text='Website',
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
        weblink_status[c] = True
    else:
        weblink_content[c].grid_remove()
        weblink_status[c] = False
    update_meta_canvas()


def error_dialog(e):
    messagebox.showerror(title='Error',
                        message=f'{e}\n\n Check your internet connection!',
                        )

def unfollow_dialog(streamer, row):
    '''Asks for confirmation, if the unfollow button is pressed. Rebuild the
    main panel, if confirmed.
    '''
    answer = add_askyesno_row(main_frame, f'\nUnfollow {streamer}?', row)
    if answer:
        twitchapi.unfollow_streamer(streamer)
        refresh_main()

def follow_dialog():
    '''Opens a text dialog and adds the entered string to the follow list.
    '''
    answer = add_askstring_row(menu_frame, 'Add streamer:')
    if answer is None or len(answer) == 0:
        return
    else:
        twitchapi.follow_streamer(answer)
        refresh_main()

def play_dialog():
    '''Opens a text dialog to play a custom stream
    '''
    streamer = add_askstring_row(menu_frame, 'Play a custom stream:')
    if streamer is None or len(streamer) == 0:
        return
    else:
        update = twitchapi.start_stream(streamer)

def refresh_main_quiet():
    global streamer_status, current_vod_panel
    try:
        streamer_status = twitchapi.extract_streamer_status()
    except Exception as e:
        error_dialog(e)

    meta_canvas.update_idletasks()  # Flush the event queue
    meta_canvas.configure(yscrollcommand=None)  # Temporarily disable scroll command

    # Clear and repopulate main_frame
    for widget in main_frame.winfo_children():
        widget.destroy()
    streamer_buttons()  # Re-populate the main_frame

    meta_canvas.update_idletasks()  # Flush the event queue
    meta_canvas.configure(yscrollcommand=scrollbar.set)  # Re-enable scroll command
    update_meta_canvas()  # Update the canvas region

    # If a VOD panel is active, refresh it
    if current_vod_panel:
        refresh_vod_panel(current_vod_panel)


def refresh_main():
    '''Runs wtwitch c and then rebuilds the main panel.'''
    twitchapi.check_status()
    global streamer_status, streamer_buttons_dict
    try:
        streamer_status = twitchapi.extract_streamer_status()
    except Exception as e:
        error_dialog(e)
    
    # Clear the dictionary before updating
    streamer_buttons_dict = {}

    for widget in main_frame.winfo_children():
        widget.destroy()
    streamer_buttons()
    update_meta_canvas()


def update_meta_canvas(force_update=False):
    if force_update or meta_canvas.bbox("all") != meta_canvas.bbox("view"):
        meta_canvas.update_idletasks()
        meta_canvas.configure(scrollregion=meta_canvas.bbox("all"))

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

def draw_main():
    '''The main window. Calls streamer_buttons() twice, to draw buttons for 
    online and offline streamers.'''
    
    meta_frame = default_frame(root)
    meta_frame.grid(row=1, column=0, sticky='nsew')
    meta_frame.columnconfigure(0, weight=1)
    meta_frame.rowconfigure(0, weight=1)
    
    global meta_canvas
    meta_canvas = default_canvas(meta_frame)
    meta_canvas.grid(row=0, column=0, sticky="nsew")
    meta_canvas.columnconfigure(0, weight=1)
    meta_canvas.rowconfigure(0, weight=1)
    
    global scrollbar
    scrollbar = ttk.Scrollbar(
        meta_frame, orient="vertical", command=meta_canvas.yview
    )
    scrollbar.grid(row=0, column=1, sticky="ns")
    meta_canvas.configure(yscrollcommand=scrollbar.set)
    
    global main_frame
    main_frame = default_frame(meta_canvas)
    main_frame.grid(row=0, column=0, sticky='nsew')
    main_frame.columnconfigure(1, weight=1)
    
    global meta_canvas_window
    meta_canvas_window = meta_canvas.create_window(
        (0, 0), window=main_frame, anchor="nw"
    )
    meta_canvas.bind(
        "<Configure>", lambda e: resize_canvas(e, meta_canvas, meta_canvas_window)
    )
    meta_canvas.bind_all("<Button-4>", lambda e: on_mouse_wheel(e, meta_canvas))
    meta_canvas.bind_all("<Button-5>", lambda e: on_mouse_wheel(e, meta_canvas))
    meta_canvas.bind_all("<MouseWheel>", lambda e: on_mouse_wheel_windows(e, 
                                                                         meta_canvas))
    # Draw main content:
    streamer_buttons()
    update_meta_canvas(True)  # Force update the canvas scroll region


def custom_player():
    '''Opens a dialog to set a custom media player.
    '''
    new_player = add_askstring_row(settings_top_frame,
                                'Enter your media player:',
                                initial_value=twitchapi.check_config()[0]
                                )
    if new_player is None or len(new_player) == 0:
        return
    else:
        twitchapi.adjust_config('player', new_player)

def custom_quality():
    '''Opens a dialog to set a custom stream quality.
    '''
    new_quality = add_askstring_row(settings_top_frame,
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

def change_info_preset(value):
    twitchapi.change_settings_file('show_info_preset', value)
    global current_expand_setting
    global preset_info_setting
    preset_info_setting = twitchapi.get_setting('show_info_preset')
    cis = current_expand_setting
    if preset_info_setting == cis or cis == 'no':
        return
    else:
        twitchapi.change_settings_file('show_info', value)
        current_expand_setting = preset_info_setting
        refresh_main_quiet()

def settings_dialog():
    '''Opens a toplevel window with four settings options.'''

    global selected_player
    selected_player = tk.StringVar()
    if twitchapi.check_config()[0] in ['mpv', 'vlc']:
        selected_player.set(twitchapi.check_config()[0])
    else:
        selected_player.set('custom')

    global selected_quality
    selected_quality = tk.StringVar()
    if twitchapi.check_config()[1] in [
        'best', '720p,720p60,480p,best', '480p,worst'
    ]:
        selected_quality.set(twitchapi.check_config()[1])
    else:
        selected_quality.set('custom')

    global settings_window
    settings_window = tk.Toplevel(master=root)
    settings_window.grid_rowconfigure(0, weight=1)
    settings_window.grid_columnconfigure(0, weight=1)
    settings_window.title('Settings')
    settings_window.transient(root)
    settings_window.grab_set()

    meta_frame = default_frame(settings_window)
    meta_frame.grid(sticky='nesw', ipady=10)

    global settings_top_frame
    settings_top_frame = default_frame(meta_frame)
    settings_top_frame.grid(row=0, column=0, sticky='nesw')
    settings_top_frame.grid_rowconfigure(0, weight=1)
    settings_top_frame.grid_columnconfigure(0, weight=1)

    qual_f = default_frame(settings_top_frame)
    qual_f.grid(row=0, column=0, sticky='nesw', ipadx=10, ipady=10)
    quality_label = default_label(qual_f, text='Video quality:')
    quality_label.grid(row=0, column=0, sticky='nesw', ipadx=10, ipady=10)
    
    high_quality = default_radiobutton(
        qual_f, text='High', value='best', variable=selected_quality,
        command=lambda: twitchapi.adjust_config('quality', 'best')
    )
    high_quality.grid(row=1, column=0, sticky='nesw', ipadx=10)
    
    mid_quality = default_radiobutton(
        qual_f, text='Medium', value='720p,720p60,480p,best',
        variable=selected_quality,
        command=lambda: twitchapi.adjust_config(
            'quality', '720p,720p60,480p,best'
        )
    )
    mid_quality.grid(row=2, column=0, sticky='nesw', ipadx=10)
    
    low_quality = default_radiobutton(
        qual_f, text='Low', value='480p,worst', variable=selected_quality,
        command=lambda: twitchapi.adjust_config('quality', '480p,worst')
    )
    low_quality.grid(row=3, column=0, sticky='nesw', ipadx=10)
    
    pick_custom_quality = default_radiobutton(
        qual_f, text='Custom', value='custom', variable=selected_quality,
        command=lambda: custom_quality()
    )
    pick_custom_quality.grid(row=4, column=0, sticky='nesw', ipadx=10)

    play_frame = default_frame(settings_top_frame)
    play_frame.grid(row=0, column=1, sticky='nesw', ipadx=10, ipady=10)
    play_label = default_label(play_frame, text='Media player:')
    play_label.grid(row=0, column=0, sticky='nesw', ipadx=10, ipady=10)
    
    pick_mpv = default_radiobutton(
        play_frame, text='mpv', value='mpv', variable=selected_player,
        command=lambda: twitchapi.adjust_config('player', 'mpv')
    )
    pick_mpv.grid(row=1, column=0, sticky='nesw', ipadx=10)
    
    pick_vlc = default_radiobutton(
        play_frame, text='VLC', value='vlc', variable=selected_player,
        command=lambda: twitchapi.adjust_config('player', 'vlc')
    )
    pick_vlc.grid(row=2, column=0, sticky='nesw', ipadx=10)
    
    pick_custom_player = default_radiobutton(
        play_frame, text='Custom', value='custom', variable=selected_player,
        command=lambda: custom_player()
    )
    pick_custom_player.grid(row=3, column=0, sticky='nesw', ipadx=10)
    
    separator = default_separator(settings_top_frame)
    separator[0].grid(row=10)
    separator[1].grid(row=11)

    settings_bottom_frame = default_frame(meta_frame)
    settings_bottom_frame.grid(row=1, column=0, sticky='nesw')

    global expand_info_setting
    expand_info_setting = tk.StringVar()
    expand_info_setting.set(preset_info_setting)
    
    info_frame = default_frame(settings_bottom_frame, borderwidth=1)
    info_frame.grid(row=0, column=0, sticky='nesw', ipadx=10)
    info_label = default_label(info_frame, text='Expand info:')
    info_label.grid(row=0, column=0, sticky='nesw', ipadx=10, ipady=10)
    
    all_info = default_radiobutton(
        info_frame, text='All', value='all', variable=expand_info_setting,
        command=lambda: [change_info_preset('all')]
    )
    all_info.grid(row=1, column=0, sticky='nesw', ipadx=10)
    
    only_online_info = default_radiobutton(
        info_frame, text='Only online', value='online',
        variable=expand_info_setting,
        command=lambda: [change_info_preset('online')]
    )
    only_online_info.grid(row=2, column=0, sticky='nesw', ipadx=10)

    theme_frame = default_frame(settings_bottom_frame, borderwidth=1)
    theme_frame.grid(row=0, column=1, sticky='nesw', ipadx=10)
    theme_label = default_label(theme_frame, text='Theme:')
    theme_label.grid(row=0, column=0, sticky='nesw', ipadx=10, ipady=10)
    
    dark_mode = default_radiobutton(
        theme_frame, text='Dark', value='dark', variable=is_gnome_darkmode,
        command=lambda: [twitchapi.change_settings_file('theme', 'dark')]
    )
    dark_mode.grid(row=1, column=0, sticky='nesw', ipadx=10)
    
    light_mode = default_radiobutton(
        theme_frame, text='Light', value='light', variable=is_gnome_darkmode,
        command=lambda: [twitchapi.change_settings_file('theme', 'light')]
    )
    light_mode.grid(row=2, column=0, sticky='nesw', ipadx=10)
    
    gnome_mode = default_radiobutton(
        theme_frame, text='GNOME', value='gnome', variable=is_gnome_darkmode,
        command=lambda: [twitchapi.change_settings_file('theme', 'gnome')]
    )
    gnome_mode.grid(row=3, column=0, sticky='nesw', ipadx=10)


def set_quick_toggle_icon(n):
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

def info_quick_toggle():
    global current_expand_setting, current_vod_panel
    if current_expand_setting == 'no':
        twitchapi.change_settings_file('show_info', preset_info_setting)
    else:
        twitchapi.change_settings_file('show_info', 'no')
    current_expand_setting = twitchapi.get_setting('show_info')
    refresh_main_quiet()

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

def custom_menu_bar():
    global current_quick_toggle_icon
    current_quick_toggle_icon = set_quick_toggle_icon(0)
    global menu_frame
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
    sep[0].grid(row=5)
    sep[1].grid(row=6)

def default_radiobutton(master, *args, **kwargs):
    if is_darkmode:
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
            bg='#FAFAFA',
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
    if is_darkmode:
        sep1 = tk.Frame(
            master,
            bg='#252525',
            height=1,
            border=0,
            **kwargs
        )
        sep2 = tk.Frame(
            master,
            bg='#484848',
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
            bg='#E3E3E3',
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
    if is_darkmode:
        canvas = tk.Canvas(
            master,
            bg='#333333',
            highlightthickness='0',
            **kwargs
        )
    else:
        canvas = tk.Canvas(
            master,
            bg='#FAFAFA',
            highlightthickness='0',
            **kwargs
        )
    return canvas

def default_frame(master, **kwargs):
    if is_darkmode:
        frame = tk.Frame(
            master,
            bg='#333333',
            **kwargs
        )
    else:
        frame = tk.Frame(
            master,
            bg='#FAFAFA',
            **kwargs
        )
    return frame

def default_label(master, *args, **kwargs):
    if is_darkmode:
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
            bg='#FAFAFA',
            fg=info_font,
            highlightthickness=0,
            **kwargs
        )
    return label

def default_button(master, *args, **kwargs):
    if is_darkmode:
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
            bg='#FAFAFA',
            fg=info_font,
            activeforeground=info_font,
            disabledforeground=info_font,
            highlightthickness=0,
            relief='flat',
            border=0,
            **kwargs
        )
    return button

def scrollbar_presets():
    scrollbar_width = 16
    if is_darkmode:
        style = ttk.Style(root)
        style.configure('Vertical.TScrollbar',
                        gripcount=0,
                        relief='flat',
                        troughrelief='flat',
                        width=scrollbar_width,
                        groovewidth=scrollbar_width,
                        arrowsize=scrollbar_width,
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
                        width=scrollbar_width,
                        groovewidth=scrollbar_width,
                        arrowsize=scrollbar_width
                        )

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
is_darkmode = twitchapi.detect_darkmode_gnome()
is_gnome_darkmode = tk.StringVar()
is_gnome_darkmode.set(twitchapi.get_setting('theme'))

scrollbar_presets()

# Import icons:
icon_files = twitchapi.icon_paths()
if is_darkmode:
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
current_expand_setting = twitchapi.get_setting('show_info')

# Store whether the weblink buttons are currently displayed:
weblink_status = {}
weblink_content = {}


current_yesno_frame = None
current_query_frame = None

custom_menu_bar()
draw_main()
root.mainloop()