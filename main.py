import subprocess
import re
from tkinter import *
from tkinter import ttk

def check_status():
    #online_status = open('online_status.txt', 'w')
    wtwitch_c = subprocess.run(['wtwitch', 'c'], capture_output=True, text=True)
    offline_streamers = re.findall('\[90m(\S*)\x1b', wtwitch_c.stdout)
    online_streamers = re.findall('\[92m(\S*)\x1b', wtwitch_c.stdout)
    print(online_streamers)
    print(offline_streamers)

check_status()

#test_stream = subprocess.run(['wtwitch', 'w', 'sips_'])

"""Create the window
root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="test").grid(column=0, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
root.mainloop()"""