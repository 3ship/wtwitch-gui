import subprocess
import re
import tkinter as tk
from tkinter import ttk

def check_status():
    #online_status = open('online_status.txt', 'w')
    wtwitch_c = subprocess.run(['wtwitch', 'c'],
                               capture_output=True, text=True)
    off_streamers1 = re.findall('\[90m(\S*)\x1b', wtwitch_c.stdout)
    off_streamers2 = re.findall('\[90m(\S*),', wtwitch_c.stdout)
    offline_streamers = off_streamers1 + off_streamers2
    offline_streamers.sort()
    online_streamers = re.findall('\[92m(\S*)\x1b', wtwitch_c.stdout)
    return online_streamers, offline_streamers
#check_status()

def fetch_vods(streamer):
    wtwitch_v = subprocess.run(['wtwitch', 'v', streamer],
                               capture_output=True, text=True)
    timestamps = re.findall('\[96m\[(\S* \S*)\]', wtwitch_v.stdout)
    titles = re.findall('\[0m\s(\S.*)\s\x1b\[93m', wtwitch_v.stdout)
    titles = [title[0:30] for title in titles]
    """index = 0
    for title in titles:
        print(title, timestamps[index])
        index += 1"""
    return titles
#print(fetch_vods("sodapoppin"))

def vod_window(streamer):
    vods = fetch_vods(streamer)
    if len(vods) == 0:
        print('no vods')
        return
    window = tk.Toplevel()
    vframe = ttk.Frame(window, padding=10)
    vframe.grid()
    vodno = 1
    for title in vods:
        live = ttk.Button(vframe,
                          text=title,
                          command=lambda
                            s=streamer,
                            vodno=vodno:
                            subprocess.run(['wtwitch', 'v', s, str(vodno)]))
        vodno += 1
        live.grid(column=0, row=vodno)

# Check the online/offline status once before window initialization:
status = check_status()

# Create the window
root = tk.Tk()
root.geometry()
sframe = ttk.Frame(root, padding=10)
sframe.grid()

# Create section of online streamers with 'watch' and last VOD button:
ttk.Label(sframe, text="Online: ").grid(column=0, row=0)
rows = 2
for index, streamer in enumerate(status[0]):
    live = ttk.Button(sframe,
                   text=streamer,
                   command=lambda s=streamer: subprocess.run(['wtwitch', 'w', s]))
    live.grid(column=0, row=index+1)
    vods = ttk.Button(sframe,
                   text="Vods",
                   command=lambda s=streamer: vod_window(s))
    vods.grid(column=1, row=index+1)
    rows += 1

# Create offline streamer section with last VOD button:
ttk.Label(sframe, text="Offline: ").grid(column=0)
offline = check_status()[1]
for index, streamer in enumerate(status[1]):
    live = ttk.Button(sframe,
                   text=streamer)
    live.grid(column=0, row=rows)
    vods = ttk.Button(sframe,
                   text="Vods",
                   command=lambda s=streamer: vod_window(s))
    vods.grid(column=1, row=rows)
    rows += 1

root.tk.mainloop()