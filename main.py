import subprocess
import re
import tkinter as tk

def call_wtwitch():
    '''Run wtwitch c and use regex to extract all streamers and their online
    status. Return a tuple of lists with both streamer groups.
    '''
    wtwitch_c = subprocess.run(['wtwitch', 'c'],
                               capture_output=True, text=True)
    #print(repr(wtwitch_c.stdout))
    off_streamers1 = re.findall('\[90m(\S*)\x1b', wtwitch_c.stdout)
    off_streamers2 = re.findall('\[90m(\S*),', wtwitch_c.stdout)
    offline_streamers = off_streamers1 + off_streamers2
    offline_streamers.sort()
    online_streamers = re.findall('\[92m(\S*)\x1b', wtwitch_c.stdout)
    return online_streamers, offline_streamers

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
                                capture_output=True, text=True
                                )
    timestamps = re.findall('\[96m\[(\S* \S*)\]', wtwitch_v.stdout)
    titles = re.findall('\]\x1b\[0m\s*(\S.*)\s\x1b\[93m', wtwitch_v.stdout)
    for i in range(len(titles)):
        if len(titles[i]) > 70:
            titles[i] = titles[i][:70] + "..."
    return timestamps, titles

def destroy_widgets(parent):
    '''Clear a frame before redrawing it
    '''
    for widget in parent.winfo_children():
        widget.destroy()

def vod_panel(streamer):
    '''Draws the VOD panel on the right side of the window. Three for loops to
    draw the timestamps, watch buttons and titles of the last 20 VODs
    '''
    # Clear the vod_panel before redrawing it, in case it was already opened
    vodframe.forget()
    vodframe.destroy()
    parent = create_vodframe()
    vods = fetch_vods(streamer)
    if len(vods[0]) == 0:
        warning_l = tk.Label(parent, text=f"{streamer} has no VODs")
        warning_l.grid(column=0, row=1, ipadx=10, ipady=10)
    vodno = 1
    for timestamp in vods[0]:
        time_l = tk.Label(parent, text=timestamp)
        time_l.grid(column=0, row=vodno, sticky='w', ipadx=20)
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
    """close_button = tk.Button(parent, text='x',
                            command=lambda p=parent:
                            [destroy_widgets(p), create_vodframe()]
                            )
    close_button.grid(column=2, row=0, sticky='ne', ipadx=3)"""

def refresh_button(parent):
    '''Button in the main panel which calls wtwitch c and redraws the panel.
    '''
    refresh = tk.Button(parent,
                        text="Refresh",
                        command=lambda root=root:
                                    [check_status(),
                                    parent.pack_forget(),
                                    main_panel(root)]
                        )
    refresh.pack(fill='x', side='top', pady=5)

def section_label(parent, text):
    '''Create text labels for window sections
    '''
    label = tk.Label(parent, text=text)
    label.pack(ipady=5)

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
                            state=state,
                            command=lambda s=streamer:
                            [subprocess.run(['wtwitch', 'w', s])]
                            )
        watch_b.pack(fill='x', side='top', padx=5)
    # VOD Buttons:
    vods = tk.Frame(parent, pady=10)
    vods.pack(side='right')
    for streamer in status[onoff]:
        vod_b = tk.Button(vods,
                        text="Vods",
                        justify='right',
                        command=lambda s=streamer:
                        vod_panel(s)
                        )
        vod_b.pack(fill='x', side='top', padx=5)

def create_vodframe():
    '''Create the vod panel separately to avoid adding a new one, when the main
    panel gets refreshed.
    '''
    global vodframe
    vodframe = tk.Frame(root)
    vodframe.pack(side='right', pady=10)
    return vodframe

def main_panel(root):
    '''Always active after window start. Segmented into a top and bottom frame
    for online and offline streamers
    '''
    mainframe = tk.Frame(root)
    mainframe.pack(fill='x', side='left')
    refresh_button(mainframe)
    # Create section of online streamers with 'watch' and VOD buttons:
    topframe = tk.Frame(mainframe)
    topframe.pack(side='top', fill='x')
    section_label(topframe, 'Online: ')
    streamer_buttons(topframe, 0, 'normal')
    # Create offline streamer section with VOD buttons:
    bottomframe = tk.Frame(mainframe)
    bottomframe.pack(side='bottom', fill='x')
    section_label(bottomframe, 'Offline: ')
    streamer_buttons(bottomframe, 1, 'disabled')

# Check the online/offline status once before window initialization:
status = call_wtwitch()
# Create the main window
root = tk.Tk()
root.title("wtwitch-gui")
main_panel(root)
create_vodframe()
root.mainloop()