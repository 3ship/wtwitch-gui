import subprocess
import re
import tkinter as tk

def check_status():
    wtwitch_c = subprocess.run(['wtwitch', 'c'],
                               capture_output=True, text=True)
    #print(repr(wtwitch_c.stdout))
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
    window = tk.Toplevel()
    window.title(f"{streamer}'s VODs")
    vframe = tk.Frame(window, padx=15, pady=15)
    vframe.grid()
    if len(vods[0]) == 0:
        warning_l = tk.Label(vframe, text=f"{streamer} has no VODs")
        warning_l.grid(column=0, row=0, ipadx=10, ipady=10)
    vodno = 1
    for timestamp in vods[0]:
        l = tk.Label(vframe, text=timestamp)
        l.grid(column=0, row=vodno, sticky='w', ipadx=8)
        vodno += 1
    vodno = 1
    for title in vods[1]:
        l = tk.Label(vframe, text=title)
        l.grid(column=1, row=vodno, sticky='w', ipadx=8)
        vodno += 1
    vodno = 1
    for title in vods[1]:
        b = tk.Button(vframe,
                      text="Watch",
                      anchor="w",
                      command=lambda s=streamer, vodno=vodno:
                      subprocess.run(['wtwitch', 'v', s, str(vodno)])
                    )
        b.grid(column=2, row=vodno, sticky='ew', ipadx=8)
        vodno += 1

def main_window(root):
    # Create section of online streamers with 'watch' and VOD buttons:
    onlineframe = tk.Frame(root, padx=15, pady=15)
    onlineframe.grid(sticky='ew')
    on_l = tk.Label(onlineframe, text="Online: ")
    on_l.grid(column=0, row=0, sticky='w')
    rows = 2
    for index, streamer in enumerate(status[0]):
        b = tk.Button(onlineframe,
                      text=streamer,
                      command=lambda s=streamer:
                      subprocess.run(['wtwitch', 'w', s])
                      )
        b.grid(column=0, row=rows, sticky='ew', ipadx=20)
        vods = tk.Button(onlineframe,
                         text="Vods",
                         command=lambda s=streamer: vod_window(s)
                         )
        vods.grid(column=1, row=rows, sticky='e', ipadx=10)
        rows += 1
    
    # Create offline streamer section with VOD buttons:
    offlineframe = tk.Frame(root, padx=15, pady=15)
    offlineframe.grid(sticky='ew')
    off_l = tk.Label(offlineframe, text="Offline: ")
    off_l.grid(column=0, sticky='w')
    offline = check_status()[1]
    for index, streamer in enumerate(status[1]):
        l = tk.Label(offlineframe, text=streamer)
        l.grid(column=0, row=rows, sticky='w', ipadx=34)
        ovods = tk.Button(offlineframe,
                         text="Vods",
                         command=lambda s=streamer: vod_window(s)
                         )
        ovods.grid(column=1, row=rows, sticky='e', ipadx=10)
        rows += 1

# Check the online/offline status once before window initialization:
status = check_status()
# Create the main window
root = tk.Tk()
root.title("wtwitch-gui")
main_window(root)
root.mainloop()