import subprocess
import re
import tkinter as tk
from tkinter import messagebox

def call_wtwitch():
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
    global status
    status = call_wtwitch()

def fetch_vods(streamer):
    wtwitch_v = subprocess.run(['wtwitch', 'v', streamer],
                                capture_output=True, text=True
                                )
    timestamps = re.findall('\[96m\[(\S* \S*)\]', wtwitch_v.stdout)
    titles = re.findall('\]\x1b\[0m\s*(\S.*)\s\x1b\[93m', wtwitch_v.stdout)
    for i in range(len(titles)):
        if len(titles[i]) > 70:
            titles[i] = titles[i][:70] + "..."
    return timestamps, titles

def button_clicked():
    messagebox.showinfo(
        title="Info",
        message="Opening player"
        )

def vod_window(streamer):
    vods = fetch_vods(streamer)
    window = tk.Toplevel()
    window.title(f"{streamer}'s VODs")
    vframe = tk.Frame(window, padx=15, pady=15)
    vframe.grid()
    if len(vods[0]) == 0:
        warning_l = tk.Label(vframe, text=f"{streamer} has no VODs")
        warning_l.grid(column=0, row=0, ipadx=10, ipady=10)
    vodno = 1
    for timestamp in vods[0]:
        time_l = tk.Label(vframe, text=timestamp)
        time_l.grid(column=0, row=vodno, sticky='w', ipadx=8, ipady=5)
        vodno += 1
    vodno = 1
    for title in vods[1]:
        watch_b = tk.Button(vframe,
                    text="Watch",
                    command=lambda s=streamer, vodno=vodno:
                    [subprocess.run(['wtwitch', 'v', s, str(vodno)])]
                    )
        watch_b.grid(column=1, row=vodno, ipadx=12)
        vodno += 1
    vodno = 1
    for title in vods[1]:
        title_l = tk.Label(vframe, text=title)
        title_l.grid(column=2, row=vodno, sticky='w', ipadx=8)
        vodno += 1

def refresh_button(parent):
    refresh = tk.Button(parent,
                        text="Refresh",
                        command=lambda root=root:
                                    [check_status(),
                                    main_window(root),
                                    parent.pack_forget(),
                                    parent.destroy()]
                        )
    refresh.pack(fill='x', side='top', pady=5)

def section_label(parent, text):
    label = tk.Label(parent, text=text)
    label.pack(ipady=5)

def streamer_buttons(parent, section, state):
    streamers = tk.Frame(parent, pady=10)
    streamers.pack(side='left')
    for streamer in status[section]:
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
    for streamer in status[section]:
        vod_b = tk.Button(vods,
                        text="Vods",
                        justify='right',
                        command=lambda s=streamer: vod_window(s)
                        )
        vod_b.pack(fill='x', side='top', padx=5)

def main_window(root):
    mainframe = tk.Frame(root)
    mainframe.pack(fill='x')
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
main_window(root)
root.mainloop()
