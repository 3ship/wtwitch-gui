import subprocess
import re
import tkinter as tk
from tkinter import ttk

def check_status():
    #online_status = open('online_status.txt', 'w')
    wtwitch_c = subprocess.run(['wtwitch', 'c'],
                               capture_output=True, text=True)
    #offline_streamers = re.findall('\[90m(\S*)\x1b', wtwitch_c.stdout)
    online_streamers = re.findall('\[92m(\S*)\x1b', wtwitch_c.stdout)
    return online_streamers

def fetch_vods(streamer):
    wtwitch_v = subprocess.run(['wtwitch', 'v', streamer],
                               capture_output=True, text=True)
    timestamps = re.findall('\[96m\[(\S* \S*)\]', wtwitch_v.stdout)
    titles = re.findall('\[0m\s(\S.*)\s\x1b', wtwitch_v.stdout)
    print(repr(wtwitch_v.stdout))
    #print(titles)
fetch_vods("sodapoppin")
#Create the window
"""root = tk.Tk()
root.geometry()
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Online: ").grid(column=0, row=0)
online = check_status()
for index, streamer in enumerate(online):
    live = ttk.Button(frm,
                   text=streamer,
                   command=lambda s=streamer: subprocess.run(['wtwitch', 'w', s]))
    live.grid(column=0, row=index+1)
    vods = ttk.Button(frm,
                   text="Vods",
                   command=lambda s=streamer: subprocess.run(['wtwitch', 'v', s]))
    vods.grid(column=index+1, row=index+1)
root.tk.mainloop()"""