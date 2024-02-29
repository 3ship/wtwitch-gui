import subprocess
import re
import tkinter as tk
from tkinter import ttk

def check_status():
    wtwitch_c = subprocess.run(['wtwitch', 'c'],
                               capture_output=True, text=True)
    off_streamers1 = re.findall('\[90m(\S*)\x1b', wtwitch_c.stdout)
    off_streamers2 = re.findall('\[90m(\S*),', wtwitch_c.stdout)
    offline_streamers = off_streamers1 + off_streamers2
    offline_streamers.sort()
    online_streamers = re.findall('\[92m(\S*)\x1b', wtwitch_c.stdout)
    return online_streamers, offline_streamers

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

def vod_window(streamer):
    vods = fetch_vods(streamer)
    if len(vods[0]) == 0:
        print('no vods')
        return
    window = tk.Toplevel()
    window.title(f"{streamer}'s VODs")
    vframe = tk.Frame(window, padx=15, pady=15)
    vframe.grid()
    vodno = 1
    for timestamp in vods[0]:
        l = ttk.Label(vframe, text=timestamp)
        l.grid(column=0, row=vodno, sticky='w', ipadx=8)
        vodno += 1
    vodno = 1
    for title in vods[1]:
        b = ttk.Button(vframe,
                       text=title,
                       command=lambda s=streamer, vodno=vodno:
                       subprocess.run(['wtwitch', 'v', s, str(vodno)])
                       )
        b.grid(column=1, row=vodno, sticky='w', ipadx=8)
        vodno += 1


# Check the online/offline status once before window initialization:
status = check_status()

# Create the main window
root = tk.Tk()
root.title("wtwitch-gui")

# Create section of online streamers with 'watch' and VOD buttons:
onlineframe = tk.Frame(root, padx=15, pady=15)
onlineframe.grid(sticky='e')
on_l = ttk.Label(onlineframe, text="Online: ")
on_l.grid(column=0, row=0, sticky='w')
rows = 2
for index, streamer in enumerate(status[0]):
    b = ttk.Button(onlineframe,
                   text=streamer,
                   command=lambda s=streamer:
                   subprocess.run(['wtwitch', 'w', s])
                   )
    b.grid(column=0, row=index+1, sticky='w', ipadx=10)
    vods = ttk.Button(onlineframe,
                   text="Vods",
                   command=lambda s=streamer: vod_window(s))
    vods.grid(column=1, row=index+1, sticky='e')
    rows += 1

# Create offline streamer section with VOD buttons:
offlineframe = tk.Frame(root, padx=15, pady=15)
offlineframe.grid()
off_l = ttk.Label(offlineframe, text="Offline: ")
off_l.grid(column=0, sticky='w')
offline = check_status()[1]
for index, streamer in enumerate(status[1]):
    l = ttk.Label(offlineframe, text=streamer)
    l.grid(column=0, row=rows, sticky='w', ipadx=8)
    vods = ttk.Button(offlineframe,
                   text="Vods",
                   command=lambda s=streamer: vod_window(s))
    vods.grid(column=1, row=rows, sticky='e')
    rows += 1

root.mainloop()