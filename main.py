import subprocess
import re
import tkinter as tk
from tkinter import ttk

def check_status():
    #online_status = open('online_status.txt', 'w')
    wtwitch_c = subprocess.run(['wtwitch', 'c'], capture_output=True, text=True)
    #offline_streamers = re.findall('\[90m(\S*)\x1b', wtwitch_c.stdout)
    online_streamers = re.findall('\[92m(\S*)\x1b', wtwitch_c.stdout)
    return online_streamers

#test_stream = subprocess.run(['wtwitch', 'w', 'sips_'])

#Create the window
root = tk.Tk()
frm = ttk.Frame(root, padding=20)
frm.grid()
ttk.Label(frm, text="Online: ").grid(column=0, row=0)
online = check_status()
for index, streamer in enumerate(online):
    b = ttk.Button(frm,
                   text=streamer,
                   command=lambda s=streamer: subprocess.run(['wtwitch', 'w', s]))
    b.grid(column=0, row=index+1)
root.tk.mainloop()

# How to create multiple buttons from variable